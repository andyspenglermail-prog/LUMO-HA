"""Strict byte/JSON validation; error details intentionally discarded."""
import json
import re


class InvalidRequest(ValueError):
    def __init__(self, status=400, code="invalid_request"):
        self.status = status
        self.code = code


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError()
        result[key] = value
    return result


def _constant(value):
    raise ValueError()


def parse_body(raw):
    if not isinstance(raw, bytes):
        raise InvalidRequest()
    if len(raw) > 16384:
        raise InvalidRequest(413, "body_too_large")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_constant=_constant)
    except (ValueError, UnicodeError, RecursionError):
        raise InvalidRequest() from None
    if not isinstance(value, dict):
        raise InvalidRequest()
    return value


def validate_turn(body):
    if set(body) != {"text", "request_id"}:
        raise InvalidRequest()
    text, request_id = body["text"], body["request_id"]
    if not isinstance(text, str) or not isinstance(request_id, str):
        raise InvalidRequest()
    try:
        size = len(text.encode("utf-8"))
    except UnicodeError:
        raise InvalidRequest() from None
    if not 1 <= size <= 8192 or re.fullmatch(r"[A-Za-z0-9_-]{8,128}", request_id) is None:
        raise InvalidRequest()


def valid_output(text):
    if not isinstance(text, str) or len(text) > 8192:
        return False
    try:
        return len(text.encode("utf-8")) <= 8192
    except UnicodeError:
        return False


def request_body(raw, operation):
    """Do not normalize bytes, keys, identifiers or text."""
    if not isinstance(raw, bytes):
        raise InvalidRequest()
    if operation == "poll":
        if raw != b"":
            raise InvalidRequest()
        return {}
    body = parse_body(raw)
    if operation == "turn":
        validate_turn(body)
    elif body != {}:
        raise InvalidRequest()
    return body
