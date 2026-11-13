"""Operate Node 6 from the Codespace without printing its credential."""
import argparse
import json
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
parser=argparse.ArgumentParser()
parser.add_argument('action',choices=['access','status','models','script','image','reel','draft','upload-private'])
parser.add_argument('--demo-dir',type=Path,default=Path.home()/'sgacd-demo')
parser.add_argument('--prompt',default='')
parser.add_argument('--title',default='SGA-CD · Deporte y cultura')
parser.add_argument('--caption',default='Formación que conecta a nuestra comunidad')
parser.add_argument('--filename',default='')
parser.add_argument('--made-for-kids',choices=['yes','no'])
args=parser.parse_args()
values=dict(line.split('=',1) for line in (args.demo_dir/'node6/node6.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
if args.action=='access':
    print(values['NODE6_TOKEN']);raise SystemExit(0)
paths={'status':'/status','models':'/providers/gemini/models','script':'/studio/script','image':'/studio/image','reel':'/studio/reel','draft':'/social/draft','upload-private':'/youtube/upload-private'}
body=None
if args.action in ['script','image']:body={'prompt':args.prompt}
elif args.action=='reel':body={'title':args.title,'caption':args.caption,'duration':4}
elif args.action in ['draft','upload-private']:
    body={'filename':args.filename,'title':args.title,'description':args.caption}
    if args.action=='draft':body['platforms']=['youtube']
    else:
        if args.made_for_kids is None:parser.error('Debes clasificar el video con --made-for-kids yes o no.')
        body.update(confirm_private=True,made_for_kids=args.made_for_kids=='yes')
request=Request('http://127.0.0.1:8606'+paths[args.action],data=json.dumps(body).encode() if body is not None else None,headers={'Authorization':'Bearer '+values['NODE6_TOKEN'],'Content-Type':'application/json'})
try:
    with urlopen(request,timeout=200) as response:result=json.load(response)
except HTTPError as error:
    result=json.loads(error.read());print(json.dumps(result,ensure_ascii=False));raise SystemExit(1)
except URLError:raise SystemExit('El nodo no está disponible en 8606.')
print(json.dumps(result,indent=2,ensure_ascii=False))
if isinstance(result,dict) and result.get('filename') and args.action in ['image','reel','draft']:
    target=args.demo_dir/'node6/downloads'/result['filename'];target.parent.mkdir(exist_ok=True)
    request=Request('http://127.0.0.1:8606/artifacts/'+result['filename'],headers={'Authorization':'Bearer '+values['NODE6_TOKEN']})
    with urlopen(request,timeout=120) as response:target.write_bytes(response.read())
    print('Archivo descargado:',target)
