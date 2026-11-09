"""Bounded byte read and strict parser failures without printing request data."""
import importlib.util,unittest
from io import BytesIO
from pathlib import Path
from django.conf import settings
if not settings.configured:settings.configure(REST_FRAMEWORK={})
from rest_framework.exceptions import ParseError
path=Path(__file__).resolve().parents[2]/'ANALEMATICA-BACKEND/core_erp/accounting/query_parser.py'
spec=importlib.util.spec_from_file_location('query_parser',path);engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
class ParserTests(unittest.TestCase):
 def parse(self,raw):return engine.AccountingQueryJSONParser().parse(BytesIO(raw))
 def test_valid_utf8_object(self):self.assertEqual(self.parse('{"question":"¿Rentabilidad?"}'.encode())['question'],'¿Rentabilidad?')
 def test_exact_byte_boundary(self):
  raw=b'{"question":"rentabilidad"}';self.assertEqual(self.parse(raw+b' '*(engine.MAX_QUERY_BYTES-len(raw)))['question'],'rentabilidad')
  with self.assertRaises(ParseError):self.parse(raw+b' '*(engine.MAX_QUERY_BYTES-len(raw)+1))
 def test_single_bounded_read(self):
  class Tracking(BytesIO):
   def read(self,n=-1):self.requested=n;return super().read(n)
  stream=Tracking(b'x'*100000)
  with self.assertRaises(ParseError):engine.AccountingQueryJSONParser().parse(stream)
  self.assertEqual(stream.requested,8193);self.assertEqual(stream.tell(),8193)
 def test_duplicate_fields_nested_and_top_level(self):
  for raw in [b'{"question":"a","question":"b"}',b'{"question":{"a":1,"a":2}}']:
   with self.assertRaises(ParseError):self.parse(raw)
 def test_constants_invalid_encoding_and_nonobjects(self):
  for raw in [b'{"question":NaN}',b'{"question":Infinity}',b'{"question":-Infinity}',b'\xff',b'[]',b'null',b'1',b'{']:
   with self.assertRaises(ParseError):self.parse(raw)
 def test_brackets_and_escaped_quotes_in_string_are_not_nesting(self):
  import json
  text='[{'*100+'"\\'+'}]'*100
  self.assertEqual(self.parse(json.dumps({'question':text}).encode())['question'],text)
 def test_excessive_nesting_is_controlled(self):
  with self.assertRaises(ParseError):self.parse(b'{"question":'+b'['*1500+b'0'+b']'*1500+b'}')
if __name__=='__main__':unittest.main()
