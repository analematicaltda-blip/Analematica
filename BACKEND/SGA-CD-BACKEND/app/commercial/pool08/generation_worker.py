"""Own offline worker. Claims are durable before inference; interrupted jobs are never auto-resubmitted."""
import argparse,os,time
from .crm import CRMError
from .generation import Generation
from .generation_store import Store
from .generation_providers import generate

def process(crm,ref):
    service=Generation(Store(crm.store),crm);item,token=service.claim(ref)
    if token is None:return item
    try:
        if item['kind']=='VIDEO':
            import json
            from .video_composition import spec,sources,render
            plan=spec(json.loads(item['prompt']));result=render(plan,item['profile']['model_digest'],sources(crm,plan))
        else:result=generate(item)
    except CRMError as exc:return service.finish(ref,token,error_code=str(exc))
    except Exception:return service.finish(ref,token,error_code='GENERATION_WORKER_FAILED')
    try:return service.finish(ref,token,result=result)
    except CRMError as exc:return service.finish(ref,token,error_code=str(exc))

def run_once(limit=10):
    if os.environ.get('COMMERCIAL_GENERATION_WORKER_ENABLED')!='1':raise CRMError('GENERATION_WORKER_DISABLED',503)
    if type(limit)!=int or not 1<=limit<=100:raise CRMError('INVALID_WORKER_LIMIT')
    from .generation_worker_context import candidates,context
    results=[]
    for ref,document in candidates():
        if len(results)>=limit:break
        try:
            with context(document) as crm:result=process(crm,ref)
            results.append({'job_id':ref,'status':result.get('status'),'code':None})
        except Exception:
            # Never log credentials, prompts, returned content or arbitrary provider exception strings.
            results.append({'job_id':ref,'status':'BLOCKED','code':'GENERATION_CONTEXT_OR_WORKER_REVIEW_REQUIRED'})
    return results

def main():
    p=argparse.ArgumentParser();p.add_argument('--watch',action='store_true');p.add_argument('--limit',type=int,default=10);args=p.parse_args()
    while True:
        print(run_once(args.limit),flush=True)
        if not args.watch:break
        time.sleep(5)
if __name__=='__main__':main()
