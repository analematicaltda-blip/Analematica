"""Local MCP stdio bridge; the client configuration never contains a credential."""
import argparse
import json
from pathlib import Path
import sys
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
parser=argparse.ArgumentParser()
parser.add_argument('--env-file',type=Path,required=True)
parser.add_argument('--url',default='http://127.0.0.1:8606')
args=parser.parse_args()
values=dict(line.split('=',1) for line in args.env_file.read_text().splitlines() if '=' in line and not line.startswith('#'))
for line in sys.stdin:
    try:
        request=json.loads(line)
        if not isinstance(request,dict):raise ValueError()
    except ValueError:
        print(json.dumps({'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'Invalid JSON request'}}),flush=True);continue
    try:
        call=Request(args.url.rstrip('/')+'/mcp',data=json.dumps(request).encode(),headers={'Authorization':'Bearer '+values['NODE6_TOKEN'],'Content-Type':'application/json','Accept':'application/json, text/event-stream'})
        with urlopen(call,timeout=120) as response:
            result=json.load(response) if response.status!=202 else None
    except (URLError,HTTPError,ValueError,KeyError):result={'jsonrpc':'2.0','id':request.get('id'),'error':{'code':-32000,'message':'Node 6 is unavailable or access was denied'}}
    if 'id' in request and result is not None:print(json.dumps(result),flush=True)
