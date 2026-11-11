"""Small strict JSON intake for read-only accounting questions only."""
import json
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ParseError

MAX_QUERY_BYTES = 8192


def unique_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON field.')
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError('Nonstandard JSON constant.')


def reject_deep_json(text):
    # Scan before json.loads: recursion limits differ between Python runtimes.
    depth = 0
    quoted = False
    escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == chr(92):
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '{[':
            depth += 1
            if depth > 8:
                raise ValueError('JSON nesting exceeds route bound.')
        elif char in '}]':
            depth -= 1


class AccountingQueryJSONParser(JSONParser):
    max_bytes = MAX_QUERY_BYTES
    def parse(self, stream, media_type=None, parser_context=None):
        raw = stream.read(self.max_bytes + 1)
        if len(raw) > self.max_bytes:
            raise ParseError(f'La consulta supera el límite de {self.max_bytes} bytes de esta ruta.')
        try:
            text = raw.decode('utf-8')
            reject_deep_json(text)
            value = json.loads(text, object_pairs_hook=unique_fields,
                               parse_constant=reject_constant)
            if not isinstance(value, dict):
                raise ValueError('JSON object required.')
            return value
        except (ValueError, RecursionError):
            raise ParseError('Consulta JSON inválida, duplicada o fuera de estructura.') from None


class AccountingScenarioJSONParser(AccountingQueryJSONParser):
    """Only bounded analytical scenarios, never a larger financial write route."""
    max_bytes = 262144
