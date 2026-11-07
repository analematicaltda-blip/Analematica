"""Loopback-only static public preview. No vault/account/login/API exposure."""
import argparse
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit,unquote
ROOT=Path(__file__).resolve().parent/'web'
FILES={'/':('index.html','text/html; charset=utf-8'),'/index.html':('index.html','text/html; charset=utf-8'),'/app.js':('app.js','text/javascript; charset=utf-8'),'/styles.css':('styles.css','text/css; charset=utf-8'),'/team.json':('team.json','application/json'),'/pending.json':('pending.json','application/json')}
class PublicPreview(BaseHTTPRequestHandler):
 def do_GET(self):
  item=FILES.get(unquote(urlsplit(self.path).path))
  if item is None:self.send_error(404);return
  file=ROOT/item[0]
  if file.is_symlink() or file.resolve().parent!=ROOT.resolve():self.send_error(404);return
  body=file.read_bytes();self.send_response(200);self.send_header('Content-Type',item[1]);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer');self.send_header('Content-Security-Policy',"default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'");self.end_headers();self.wfile.write(body)
 def log_message(self,*args):pass
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8556);args=parser.parse_args()
 if not 0<=args.port<=65535:parser.error('invalid port')
 server=ThreadingHTTPServer(('127.0.0.1',args.port),PublicPreview)
 print('Public wallet preview: http://127.0.0.1:'+str(server.server_port),flush=True)
 server.serve_forever()
