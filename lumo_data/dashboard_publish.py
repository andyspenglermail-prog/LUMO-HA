"""Create-only native dashboard publication. No update/delete/retry facility.

One-use ingress authorization is separate from connector authorization. Every
mutation checks the requesting user's current HA role and immutable options.
"""
import re
import secrets
import time
from client import ReadError
from dashboard_reads import validate_configuration

MAX_BODY = 1048576 + 4096
META = ('url_path', 'title', 'icon', 'require_admin', 'show_in_sidebar')


class DashboardSessions:
    def __init__(self):
        self.tokens = {}

    def issue(self, user, policy):
        now = time.monotonic()
        self.tokens = {k:v for k,v in self.tokens.items() if v[2] > now}
        if len(self.tokens) >= 1024:
            raise ReadError('dashboard_busy', 429)
        token = secrets.token_urlsafe(32)
        self.tokens[token] = (user, policy, now + 120)
        return {'token':token, 'expiresIn':120}

    def consume(self, token, user, policy):
        value = self.tokens.pop(token, None)
        if value is None or value[0] != user or value[1] is not policy or value[2] <= time.monotonic():
            raise ReadError('invalid_dashboard_token', 403)


def require_admin(rows, user):
    if type(rows) is not list or len(rows) > 1024:
        raise ReadError('dashboard_admin_unavailable')
    matches = [row for row in rows if type(row) is dict and row.get('id') == user]
    if len(matches) != 1:
        raise ReadError('dashboard_admin_required', 403)
    row = matches[0]
    groups = row.get('group_ids')
    if (row.get('is_active') is not True or type(row.get('is_owner')) is not bool
            or type(groups) is not list or len(groups) > 64
            or any(type(group) is not str for group in groups)
            or not (row['is_owner'] or 'system-admin' in groups)):
        raise ReadError('dashboard_admin_required', 403)


def validate_request(value, policy):
    if type(value) is not dict or set(value) != set(META) | {'token', 'config'}:
        raise ReadError('invalid_request', 400)
    if type(value['token']) is not str or not re.fullmatch(r'[A-Za-z0-9_-]{43}', value['token']):
        raise ReadError('invalid_dashboard_token', 403)
    title = value['title']
    if type(title) is not str or not 1 <= len(title) <= 256 or not title.strip() or any(ord(c) < 32 for c in title):
        raise ReadError('invalid_dashboard_title', 400)
    path = value['url_path']
    if type(path) is not str or len(path) > 128 or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)+', path):
        raise ReadError('invalid_dashboard_path', 400)
    icon = value['icon']
    if type(icon) is not str or len(icon) > 80 or not re.fullmatch(r'mdi:[a-z0-9]+(?:-[a-z0-9]+)*', icon):
        raise ReadError('invalid_dashboard_icon', 400)
    if any(type(value[k]) is not bool for k in ('require_admin', 'show_in_sidebar')):
        raise ReadError('invalid_request', 400)
    validate_configuration(value['config'], policy, allow_adjacent_unheaded=True)


def publish(client, value, user, policy, guard):
    validate_request(value, policy)
    metadata = {k:value[k] for k in META}
    stage = 'preflight'
    try:
        with client._websocket() as wire:
            counter = 0

            def command(kind, **fields):
                nonlocal counter
                counter += 1
                if kind == 'lovelace/config/save':
                    wire.dashboard_save(counter, fields['url_path'], fields['config'])
                else:
                    wire.json_send({'id':counter, 'type':kind, **fields})
                response = wire.message(MAX_BODY)
                if response.get('type') != 'result' or type(response.get('id')) is not int or response['id'] != counter or type(response.get('success')) is not bool:
                    raise ReadError('dashboard_protocol_error')
                return response

            def read(kind, expected, **fields):
                response = command(kind, **fields)
                if response['success'] is not True or type(response.get('result')) is not expected:
                    raise ReadError('dashboard_read_unavailable')
                return response['result']

            def authorize():
                guard()
                require_admin(read('config/auth/list', list), user)
                guard()

            def listing():
                rows = read('lovelace/dashboards/list', list)
                if len(rows) > 256 or any(type(row) is not dict or type(row.get('url_path')) is not str for row in rows):
                    raise ReadError('dashboard_read_unavailable')
                paths = [row['url_path'] for row in rows]
                if len(paths) != len(set(paths)):
                    raise ReadError('dashboard_read_unavailable')
                return rows

            def exact_row(row):
                return (type(row) is dict and row.get('mode') == 'storage'
                        and type(row.get('id')) is str and 1 <= len(row['id']) <= 256
                        and all(type(row.get(k)) is type(metadata[k]) and row[k] == metadata[k] for k in META))

            authorize()
            if any(row['url_path'] == value['url_path'] for row in listing()):
                raise ReadError('dashboard_collision', 409)
            authorize()
            stage = 'creating'  # A failed send cannot prove no bytes arrived.
            response = command('lovelace/dashboards/create', mode='storage', **metadata)
            if response['success'] is not True:
                error = response.get('error')
                code = error.get('code') if type(error) is dict else None
                # Only command-validation/auth refusals prove no create ran.
                if code in ('invalid_format', 'unauthorized', 'unknown_command'):
                    stage = 'preflight'
                    raise ReadError('dashboard_create_rejected', 409)
                raise ReadError('dashboard_create_unknown')
            stage = 'created'
            created = response.get('result')
            if not exact_row(created):
                raise ReadError('dashboard_created_readback_failed')
            # Pin the newly returned ID before saving. Never select an existing ID.
            rows = listing()
            matches = [row for row in rows if row['url_path'] == value['url_path']]
            if len(matches) != 1 or not exact_row(matches[0]) or matches[0]['id'] != created['id']:
                raise ReadError('dashboard_created_readback_failed')
            authorize()
            empty = command('lovelace/config', url_path=value['url_path'])
            if (empty['success'] is not False or type(empty.get('error')) is not dict
                    or empty['error'].get('code') != 'config_not_found'):
                raise ReadError('dashboard_created_readback_failed')
            authorize()
            stage = 'saving'
            response = command('lovelace/config/save', url_path=value['url_path'], config=value['config'])
            if response['success'] is not True:
                error = response.get('error')
                code = error.get('code') if type(error) is dict else None
                if code in ('invalid_format', 'unauthorized', 'unknown_command', 'config_not_found'):
                    stage = 'save_rejected'
                    raise ReadError('dashboard_created_save_failed')
                raise ReadError('dashboard_created_save_unknown')
            if 'result' not in response or response['result'] is not None:
                raise ReadError('dashboard_created_save_unknown')
            stage = 'saved'
            authorize()
            rows = listing()
            matches = [row for row in rows if row['url_path'] == value['url_path']]
            if len(matches) != 1 or not exact_row(matches[0]) or matches[0]['id'] != created['id']:
                raise ReadError('dashboard_created_readback_failed')
            actual = read('lovelace/config', dict, url_path=value['url_path'])
            # JSON canonical comparison distinguishes bool/int and extra keys.
            import json
            def canonical(config):
                return json.dumps(config, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
            if canonical(actual) != canonical(value['config']):
                raise ReadError('dashboard_created_readback_failed')
            guard()
            return {'created':True, 'verified':True, 'dashboard':metadata}
    except (ReadError, OSError, ValueError, TypeError, RecursionError, UnicodeError) as error:
        if stage == 'creating':
            raise ReadError('dashboard_create_unknown') from None
        if stage != 'preflight':
            if isinstance(error, ReadError) and error.status == 403:
                raise ReadError('dashboard_created_authorization_changed', 403) from None
            if stage == 'saving':
                raise ReadError('dashboard_created_save_unknown') from None
            if stage == 'save_rejected':
                raise ReadError('dashboard_created_save_failed') from None
            raise ReadError('dashboard_created_readback_failed') from None
        if isinstance(error, ReadError):
            raise
        raise ReadError('dashboard_read_unavailable') from None
