"""Read-only review of all24 commercial tasks; never awards progress or deploys.

Source presence, historical evidence and a current reproducible regression are
separate observations. A mapped test is not proof of complete acceptance.
"""
import argparse,hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
MODULES=('contract','access_admin','crm','opportunities','pricing','quotations','sales','payments','after_sales','landings','landing_capture','media_library','generation','video_composition','media_adaptation','email_campaigns','mobile_messages','publishing','inbox','ads','army','analytics',None,'operations')
PREFIXES=(('pool08_contract','pool08_native_http'),('pool08_access_',),('pool08_crm_',),('pool08_opportunities_',),('pool08_pricing_',),('pool08_quotations_',),('pool08_sales_',),('pool08_payments_',),('pool08_after_sales_',),('pool08_landings_',),('pool08_capture_',),('pool08_library_',),('pool08_generation_',),('pool08_video_',),('pool08_adaptation_',),('pool08_email_campaign_',),('pool08_mobile_',),('pool08_publishing_',),('pool08_inbox_',),('pool08_ads_',),('pool08_army_','commercial_staff_truth'),('pool08_analytics_',),('pool08_workspace_','pool08_native_ui'),('pool08_operations_','pool08_recovery_','pool08_offline_browser','commercial_gate','offline_asset_regression'))
BACKENDS=('BACKEND/SGA-CD-BACKEND/app/commercial/pool08','BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/pool08','BACKEND/ANALEMATICA-BACKEND/gestion_comercial/pool08')
FRONTENDS=('FRONTEND/SGA-CD-WEB.git/js/commercial-crm.js','FRONTEND/SGA-ERP-TUR-FRONTEND/public/js/commercial-crm.js','FRONTEND/ANALEMATICA-FRONTEND/js/commercial-crm.js')
def module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def qualify_report(report,current):
 """A checksum-consistent file can still describe a failed or stale run."""
 if not report or not isinstance(current,str) or not current:return False
 rows=report.get('results',[]);ids=[v.get('id') for v in rows]
 return bool(rows and report.get('local_checks_complete') is True and report.get('source_stable') is True
             and report.get('source_digest_before')==report.get('source_digest_after')==current
             and all(isinstance(name,str) and name for name in ids) and len(ids)==len(set(ids))
             and all(v.get('status')=='PASSED' and not v.get('skipped') and not v.get('log_truncated')
                     and not v.get('log_write_error') for v in rows))

def safe_blob(relative):
 path=Path(relative)
 if path.is_absolute() or '..' in path.parts:raise ValueError('EVIDENCE_PATH_OUTSIDE_REPOSITORY')
 target=ROOT/path
 if target.is_symlink() or not target.resolve().is_relative_to(ROOT.resolve()):raise ValueError('EVIDENCE_PATH_OUTSIDE_REPOSITORY')
 if target.stat().st_size>32*1024*1024:raise ValueError('EVIDENCE_SIZE_LIMIT')
 return target.read_bytes()

def historical_quality(reference,runner):
 entry=json.loads(safe_blob(reference['artifact']))
 for key in reference['entry'].split('.'):entry=entry[key]
 q=entry['quality']
 if 'artifact' in q:
  raw=safe_blob(q['artifact'])
  if hashlib.sha256(raw).hexdigest()!=q['sha256']:raise ValueError('HISTORICAL_QUALITY_HASH_MISMATCH')
  directory=Path(q['artifact']).parent
  # Check parent confinement before the generic artifact verifier follows files.
  safe_blob(directory/'checksums.json');safe_blob(directory/'source-manifest.json')
  runner.verify_artifacts(ROOT/directory);report=json.loads(raw);mode='HASHED_REPORT_AND_RAW_ARTIFACTS'
 else:
  report=q;manifest=entry['quality_source_manifest']
  if runner.digest(manifest)!=report['source_digest_before']:raise ValueError('HISTORICAL_SOURCE_MANIFEST_MISMATCH')
  mode='HASHED_REGISTRY_EMBEDDED_REPORT_ONLY'
 if not qualify_report(report,report.get('source_digest_before')):raise ValueError('HISTORICAL_RUN_NOT_QUALIFIED')
 return {'integrity_verified':True,'mode':mode,'source_digest':report['source_digest_after'],
         'raw_logs_verified':mode=='HASHED_REPORT_AND_RAW_ARTIFACTS',
         'independent_authenticity_verified':False}

def evaluate(quality=None):
 validator=module(ROOT/'ANALISIS/gestion-comercial/tools/update_plan.py','commercial_audit_plan');runner=module(Path(__file__).with_name('verify_local.py'),'commercial_audit_runner')
 plan_path=ROOT/'ANALISIS/gestion-comercial/plan-pool08.json';plan=json.loads(plan_path.read_text());progress=validator.measure(plan)
 if [t['id'] for t in plan['tasks']]!=['GC-%03d'%i for i in range(1,25)]:raise ValueError('Expected original24-task scope')
 current=runner.digest(runner.source_manifest());report=None
 if quality:
  runner.verify_artifacts(quality);report=json.loads((Path(quality)/'report.json').read_text())
 accepted=set(progress['accepted_task_ids']);rows=[];credits=[];historical_cache={};qualified=qualify_report(report,current)
 for index,task in enumerate(plan['tasks']):
  paths=[base+'/'+MODULES[index]+'.py' for base in BACKENDS] if MODULES[index] else list(FRONTENDS)
  if task['id']=='GC-009':paths[0]=BACKENDS[0]+'/sales_bridge.py'
  tests=[{'id':v['id'],'state':v['status'],'log_sha256':v['log_sha256']} for v in report['results'] if v['id'].startswith(PREFIXES[index])] if report else []
  for milestone in task['milestones']:
   if milestone['state']!='VERIFICADO':continue
   proofs=[]
   for reference in milestone['evidence']:
    key=(reference['artifact'],reference['entry'],reference['entry_sha256'])
    if key not in historical_cache:
     try:historical_cache[key]=historical_quality(reference,runner)
     except (OSError,ValueError,KeyError,TypeError):historical_cache[key]={'integrity_verified':False,'error':'HISTORICAL_ARTIFACT_REVIEW_REQUIRED','raw_logs_verified':False}
    proofs.append({**historical_cache[key],'reference':reference})
   credits.append({'ordinal':len(credits)+1,'task_id':task['id'],'milestone_id':milestone['id'],
                   'stage':milestone['stage'],'declared_reference_verified':True,'historical_evidence':proofs,
                   'historical_artifacts_verified':all(p['integrity_verified'] for p in proofs),
                   'current_related_regression_passed':bool(qualified and tests and all(t['state']=='PASSED' for t in tests)),
                   'functional_scope_independently_reaccepted':False,'full_task_acceptance':task['id'] in accepted,
                   'development_pending':task['missing'],'external_requirements':task['external_requirements']})
  rows.append({'id':task['id'],'title':task['title'],'declared_state':task['state'],'milestones':[{'id':v['id'],'stage':v['stage'],'state':v['state']} for v in task['milestones']],'full_acceptance_evidenced':task['id'] in accepted,'scope_still_pending':task['missing'],'external_requirements':task['external_requirements'],'dependencies_without_full_acceptance':[v for v in task['dependencies'] if v not in accepted],'source_observations':[{'path':name,'present':(ROOT/name).is_file(),'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest() if (ROOT/name).is_file() else None} for name in paths],'mapped_tests':tests,'mapped_test_scope_complete':False,'source_presence_awards_credit':False})
 return {'schema':'commercial24-review-v1','plan_sha256':hashlib.sha256(plan_path.read_bytes()).hexdigest(),'source_digest_current':current,'progress':progress,'tasks':rows,'credited_milestones_review':credits,'remaining_plan_steps':plan['remaining_work_plan']['steps'],'quality':{'provided':bool(report),'current_regression_qualified':qualified,'historical_artifact_failures':[c['milestone_id'] for c in credits if not c['historical_artifacts_verified']],'current_sources_match':bool(report and report['source_digest_after']==current),'source_stable':bool(report and report['source_stable']),'local_checks_complete':bool(report and report['local_checks_complete']),'missing_mapped_tests':[v['id'] for v in rows if not v['mapped_tests']],'non_passed':[{k:v[k] for k in ('id','status')} for v in report['results'] if v['status']!='PASSED'] if report else []},'new_progress_credit':0,'production_enabled':False,'limitations':['Test mapping identifies related executions, not complete acceptance or all business cases.','Source files and passing laboratory tests never establish provider, hardware or professional acceptance.','Historical state remains historical; current source compatibility is reported separately.']}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--quality',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();result=evaluate(a.quality)
 with a.output.open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps({'tasks_reviewed':len(result['tasks']),'accepted':result['progress']['fully_accepted_tasks'],'milestones':result['progress']['completed_milestones'],'current_sources_match':result['quality']['current_sources_match'],'new_credit':0,'production_enabled':False}))
