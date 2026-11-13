"""Read-only inventory and service discovery. Never downloads weights or sends generation prompts."""
import argparse,json
from pathlib import Path
import httpx

def inspect_runtime():
    result=[]
    for name,port,path in [('ollama',11434,'/api/tags'),('colibri',8080,'/v1/models'),('open-generative-ai',3000,'/api/health'),('skyreels-v2',8090,'/health'),('gemini-node6',8606,'/health')]:
        row={'engine':name,'endpoint':'http://127.0.0.1:'+str(port),'status':'UNREACHABLE','inference_verified':False}
        try:
            with httpx.Client(timeout=2,follow_redirects=False,trust_env=False) as c:
                with c.stream('GET',row['endpoint']+path) as response:
                    row['http_status']=response.status_code;raw=bytearray()
                    for chunk in response.iter_bytes():
                        raw.extend(chunk)
                        if len(raw)>2*1024*1024:raise ValueError()
                if response.status_code==200:
                    body=json.loads(raw);row['status']='HTTP_AVAILABLE_NOT_QUALIFIED'
                    if name=='ollama' and isinstance(body,dict):row['models']=[{'name':x.get('name'),'digest':x.get('digest')} for x in body.get('models',[]) if isinstance(x,dict)]
                    if name=='colibri' and isinstance(body,dict):row['models']=[{'name':x.get('id')} for x in body.get('data',[]) if isinstance(x,dict)]
                else:row['status']='AUTHENTICATION_OR_CONFIGURATION_REQUIRED'
        except (httpx.HTTPError,ValueError,TypeError):pass
        result.append(row)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--probe',action='store_true');args=p.parse_args();catalog=json.loads(Path(__file__).with_name('generation_catalog.json').read_text());print(json.dumps({'catalog':catalog,**({'runtime':inspect_runtime()} if args.probe else {})},ensure_ascii=False,indent=2))
