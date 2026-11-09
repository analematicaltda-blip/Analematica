"""Bounded JSON reader for envelope inspection only; no multipart/file upload path."""
from io import BytesIO
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ParseError
from .fiscal_envelope import MAX_WIRE_BYTES

class FiscalEnvelopeJSONParser(JSONParser):
    def parse(self,stream,media_type=None,parser_context=None):
        raw=stream.read(MAX_WIRE_BYTES+1)
        if len(raw)>MAX_WIRE_BYTES:raise ParseError('El sobre supera el límite de esta ruta. No se almacenó el documento.')
        return super().parse(BytesIO(raw),media_type,parser_context)
