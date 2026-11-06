"""Bounded Core adapter. Native bootstrap fixes origin; constructor is a private diagnostic seam.
Only the fixed dashboard/permission reads use this transport. No retry,
HTTP proxy, controls, publication, TLS bypass, logging or public arbitrary API.
"""
import base64
import hashlib
import http.client
import json
import os
import re
import socket
import ssl
import struct
import time
from contextlib import contextmanager
MAX_BYTES = 16 * 1024 * 1024
MAX_SECONDS = 15
ENTITY = re.compile('[a-z_][a-z0-9_]*\\.[a-z0-9_]{1,254}')

class ReadError(Exception):

    def __init__(self, code='upstream_unavailable', status=502):
        self.code = code
        self.status = status
        super().__init__(code)

def parse_json(data):

    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise ValueError()
            result[k] = v
        return result

    def constant(_):
        raise ValueError()
    return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)

class Wire:
    """Single RFC6455 connection, bounded total traffic, frames and wall deadline."""

    def __init__(self, sock, deadline):
        self.sock = sock
        self.deadline = deadline
        self.bytes = 0
        self.frames = 0

    def budget(self):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise ReadError('upstream_timeout')
        self.sock.settimeout(min(3, remaining))

    def exact(self, n):
        if self.bytes + n > MAX_BYTES:
            raise ReadError('response_limit')
        self.bytes += n
        result = bytearray()
        while len(result) < n:
            self.budget()
            part = self.sock.recv(n - len(result))
            if not part:
                raise ReadError()
            result.extend(part)
        return bytes(result)

    def send(self, data, opcode=1, *, limit=8192):
        self.budget()
        if len(data) > limit:
            raise ReadError('request_limit')
        mask = os.urandom(4)
        length = len(data)
        prefix = bytes([128 | opcode, 128 | (length if length < 126 else 126 if length < 65536 else 127)])
        if 126 <= length < 65536:
            prefix += struct.pack('!H', length)
        elif length >= 65536:
            prefix += struct.pack('!Q', length)
        self.sock.sendall(prefix + mask + bytes((b ^ mask[i % 4] for i, b in enumerate(data))))

    def json_send(self, value):
        self.send(json.dumps(value, separators=(',', ':')).encode())

    def message(self, max_bytes=MAX_BYTES):
        parts = []
        size = 0
        fragmented = False
        while True:
            self.frames += 1
            if self.frames > 2048:
                raise ReadError('response_limit')
            a, b = self.exact(2)
            fin = bool(a & 128)
            opcode = a & 15
            n = b & 127
            if a & 112 or b & 128:
                raise ReadError('invalid_websocket')
            if n == 126:
                n = struct.unpack('!H', self.exact(2))[0]
                if n < 126:
                    raise ReadError('invalid_websocket')
            elif n == 127:
                n = struct.unpack('!Q', self.exact(8))[0]
                if n < 65536 or n >> 63:
                    raise ReadError('invalid_websocket')
            if opcode >= 8:
                if not fin or n > 125:
                    raise ReadError('invalid_websocket')
                data = self.exact(n)
                if opcode == 9:
                    self.send(data, 10)
                    continue
                if opcode == 10:
                    continue
                raise ReadError('upstream_closed')
            if opcode not in (0, 1) or (opcode == 0) != fragmented:
                raise ReadError('invalid_websocket')
            size += n
            if size > max_bytes:
                raise ReadError('response_limit')
            parts.append(self.exact(n))
            if fin:
                value = parse_json(b''.join(parts).decode('utf-8'))
                if type(value) is not dict:
                    raise ReadError('invalid_websocket')
                return value
            fragmented = True

class CoreClient:

    def __init__(self, token, *, host='supervisor', port=80, tls=False, api_prefix='/core/api/', ws_path='/core/websocket'):
        if not isinstance(token, str) or not re.fullmatch('[!-~]{1,4096}', token):
            raise ReadError('credential_unavailable', 503)
        if not isinstance(host, str) or not re.fullmatch('[A-Za-z0-9.:-]{1,253}', host) or type(port) is not int or (not 1 <= port <= 65535) or (type(tls) is not bool):
            raise ReadError('invalid_origin')
        if api_prefix not in ('/core/api/', '/api/') or ws_path not in ('/core/websocket', '/api/websocket'):
            raise ReadError('invalid_origin')
        self._token = token
        self.host = host
        self.port = port
        self.tls = tls
        self.api_prefix = api_prefix
        self.ws_path = ws_path

    def __repr__(self):
        return '<CoreClient private credentials>'

    @contextmanager
    def _websocket(self):
        sock = None
        try:
            deadline = time.monotonic() + MAX_SECONDS
            sock = socket.create_connection((self.host, self.port), timeout=3)
            if self.tls:
                sock = ssl.create_default_context().wrap_socket(sock, server_hostname=self.host)
            wire = Wire(sock, deadline)
            key = base64.b64encode(os.urandom(16)).decode()
            authority = ('[' + self.host + ']' if ':' in self.host else self.host) + ':' + str(self.port)
            wire.budget()
            sock.sendall(f'GET {self.ws_path} HTTP/1.1\r\nHost: {authority}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Version: 13\r\nSec-WebSocket-Key: {key}\r\n\r\n'.encode('ascii'))
            header = b''
            while not header.endswith(b'\r\n\r\n'):
                if len(header) >= 8192:
                    raise ReadError('response_limit')
                header += wire.exact(1)
            lines = header.decode('ascii').split('\r\n')
            headers = {}
            if not re.fullmatch('HTTP/1\\.[01] 101 [^\\r\\n]*', lines[0]):
                raise ReadError('websocket_handshake')
            for line in lines[1:-2]:
                k, separator, v = line.partition(':')
                k = k.lower()
                if not separator or k in headers or (not re.fullmatch('[a-z0-9-]+', k)):
                    raise ReadError('websocket_handshake')
                headers[k] = v.strip()
            expected = base64.b64encode(hashlib.sha1((key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
            if headers.get('upgrade', '').lower() != 'websocket' or headers.get('connection', '').lower() != 'upgrade' or headers.get('sec-websocket-accept') != expected or ('sec-websocket-extensions' in headers) or ('sec-websocket-protocol' in headers):
                raise ReadError('websocket_handshake')
            if wire.message().get('type') != 'auth_required':
                raise ReadError('upstream_auth')
            wire.json_send({'type': 'auth', 'access_token': self._token})
            if wire.message().get('type') != 'auth_ok':
                raise ReadError('upstream_auth')
            yield wire
        except ReadError:
            raise
        except (OSError, ValueError, TypeError, RecursionError, UnicodeError):
            raise ReadError() from None
        finally:
            if sock is not None:
                sock.close()

    def _ws_reads(self, commands, result_type, error_code, max_bytes=MAX_BYTES):
        with self._websocket() as wire:
            results = []
            for i, command in enumerate(commands, 1):
                wire.json_send({'id': i, **command})
                value = wire.message(max_bytes)
                if value.get('type') != 'result' or type(value.get('id')) is not int or value['id'] != i:
                    raise ReadError(error_code)
                if command['type'] == 'lovelace/config' and value.get('success') is False and (type(value.get('error')) is dict) and (value['error'].get('code') == 'config_not_found'):
                    raise ReadError('dashboard_not_found', 404)
                if value.get('success') is not True or type(value.get('result')) is not result_type:
                    raise ReadError(error_code)
                results.append(value['result'])
            return results
