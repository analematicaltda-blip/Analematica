"""Explicit isolated ORM benchmark, never selects a project/customer database."""
import argparse,hashlib,importlib.util,json,os,platform,runpy,sys,time,uuid
from pathlib import Path
from datetime import datetime,timezone
from accounting_benchmark_metrics import summarize,classification_metrics
ROOT=Path(__file__).resolve().parents[2]

def run(samples):
    if type(samples) is not int or not 5<=samples<=100:raise ValueError('Use5 to100 measured transactions.')
    if 'django' in sys.modules:raise ValueError('Run in a new process; do not reuse a configured application database.')
    spec=importlib.util.spec_from_file_location('quality',ROOT/'INTEGRACIONES/operacion/verify_local.py');quality=importlib.util.module_from_spec(spec);spec.loader.exec_module(quality)
    before=quality.digest(quality.source_manifest())
    fixture=runpy.run_path(str(ROOT/'BACKEND/deployment/tests/accounting_commercial_tax_check.py'),run_name='isolated_benchmark_fixture')
    from django.db import connection
    from apps.core_erp.accounting import commercial_tax_posting as engine
    from apps.core_erp.accounting.tax_register import reconcile_tax_register
    from apps.core_erp.accounting.models import JournalEntry,LedgerEntry
    # The fixture must select fresh temporary SQLite, not an arbitrary supplied DSN.
    if connection.vendor!='sqlite' or connection.settings_dict['NAME']!=':memory:':raise ValueError('Expected the isolated in-memory fixture database.')
    case=fixture['CommercialTaxChecks']();case.setUp()
    observations={key:[] for key in ['review','post','replay','tax_register']};invariants=[]
    def measure(kind,operation):
        begin=time.perf_counter_ns()
        try:result=operation()
        except Exception:
            observations[kind].append({'duration_ns':time.perf_counter_ns()-begin,'ok':False});raise
        observations[kind].append({'duration_ns':time.perf_counter_ns()-begin,'ok':True});return result
    # No warm-up transactions are hidden; samples start at an empty company book.
    for index in range(samples):
        case.fact['document_id']=str(uuid.uuid5(uuid.NAMESPACE_URL,'synthetic-accounting-benchmark-document-'+str(index)))
        case.fact['document_digest']=hashlib.sha256(('synthetic-fixture-document-'+str(index)).encode()).hexdigest()
        reviewed=measure('review',case.review)
        posted=measure('post',lambda:case.post(reviewed))
        replay=measure('replay',lambda:case.post(reviewed))
        report=measure('tax_register',lambda:reconcile_tax_register(case.company.pk,account_id=str(case.input_tax.pk),since=case.base.day.isoformat(),until=case.base.day.isoformat()))
        assert posted['journal_id']==replay['journal_id'] and replay['replayed'] and report['tax_by_kind']['INPUT_TAX']==format(19*(index+1),'.2f') and report['unattributed_normal_movement']=='0.00'
        invariants.append({'same_journal_on_replay':True,'tax_matches_posted_components':True})
    assert JournalEntry.plain_objects.filter(tenant=case.company).count()==samples and LedgerEntry.plain_objects.filter(tenant=case.company).count()==samples*4
    after=quality.digest(quality.source_manifest())
    if before!=after:raise ValueError('Source changed during benchmark; measurements are not qualified.')
    dataset={'schema':'sgacd-synthetic-commercial-benchmark-v1','documents':samples,'items_per_document':1,'net_cop':'100.00','input_tax_bps':1900,'withholding_bps':250,'policy_scope':'SYNTHETIC_OWNER_DECLARED_NOT_STATUTORY','database':'disposable in-memory SQLite ORM fixture','sequential_workers':1,'warmup_samples_excluded':0,'physical_end_to_end':False}
    return {'schema':'sgacd-accounting-benchmark-v1','created_at':datetime.now(timezone.utc).isoformat(),'source_digest':before,'source_stable':True,'dataset':dataset,'dataset_digest':hashlib.sha256(json.dumps(dataset,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'hardware':{'os':platform.system(),'machine':platform.machine(),'python':platform.python_version(),'logical_cpus_visible':os.cpu_count(),'concurrency':1},'flows':{key:summarize(rows) for key,rows in observations.items()},'invariants':{'evaluated_transactions':len(invariants),'journal_count_matches':True,'replay_never_duplicates':True,'tax_matches_every_cut':True},'classification':classification_metrics(None),'production_ready':False,'limits':['In-process sequential SQLite ORM measurements; excludes HTTP, devices and provider latency','Synthetic workload, not representative production load or a concurrency/soak test','No machine-learning classifier was executed; no99.8% precision claim','A local250ms result is not a hardware-independent SLA']}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--synthetic-local',action='store_true',required=True);parser.add_argument('--samples',type=int,default=10);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    target=args.output
    if not target.is_absolute() or target.resolve().is_relative_to(ROOT) or target.exists() or any(p.is_symlink() for p in [target,*target.parents]):parser.error('Use a new absolute private output file outside the repository, without symlinks.')
    report=run(args.samples)
    with open(target,'x',opener=lambda name,flags:os.open(name,flags,0o600)) as stream:json.dump(report,stream,ensure_ascii=False,indent=2)
    print(json.dumps({'report':str(target),'production_ready':False,'flows':report['flows'],'classification_status':report['classification']['status']}))
if __name__=='__main__':main()
