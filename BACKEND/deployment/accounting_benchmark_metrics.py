"""Bounded financial benchmark statistics; failures/abstentions never disappear."""
from decimal import Decimal,localcontext,Context
import re

def summarize(samples,*,target_ms='250.000'):
    if not isinstance(samples,list) or not 1<=len(samples)<=10000:raise ValueError('Bounded nonempty observations required.')
    if not isinstance(target_ms,str) or not re.fullmatch(r'(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,6})?',target_ms):raise ValueError('Exact positive latency target text required.')
    target=Decimal(target_ms)
    if not target.is_finite() or target<=0:raise ValueError('Positive finite latency target required.')
    durations=[];errors=0
    for sample in samples:
        if not isinstance(sample,dict) or set(sample)!={'duration_ns','ok'} or type(sample['duration_ns']) is not int or not 0<=sample['duration_ns']<=18446744073709551615 or type(sample['ok']) is not bool:raise ValueError('Explicit duration and outcome required.')
        durations.append(sample['duration_ns']);errors+=not sample['ok']
    durations.sort()
    with localcontext(Context(prec=40)) as context:
        context.prec=40
        ms=lambda value:format((Decimal(value)/1000000).quantize(Decimal('0.001')),'.3f')
        rank=lambda percentile:durations[max(0,(len(durations)*percentile+99)//100-1)]
        return {'samples':len(samples),'successes':len(samples)-errors,'errors':errors,'minimum_ms':ms(durations[0]),'p50_ms':ms(rank(50)),'p95_ms':ms(rank(95)),'p99_ms':ms(rank(99)),'maximum_ms':ms(durations[-1]),'mean_ms':ms(Decimal(sum(durations))/len(durations)),'target_ms':format(target,'f'),'all_samples_within_target':max(durations)<=target*1000000,'local_target_met':errors==0 and max(durations)<=target*1000000,'percentile_method':'NEAREST_RANK','includes_failed_attempt_durations':True,'within_target_samples':sum(d<=target*1000000 for d in durations),'over_target_samples':sum(d>target*1000000 for d in durations)}

def classification_metrics(records):
    if records is None:return {'status':'NOT_EVALUATED','samples':0,'accuracy_percent':None,'threshold_99_8_verified':False,'reason':'No authorized labelled predictions and model evaluation supplied.'}
    if not isinstance(records,list) or not 1<=len(records)<=10000:raise ValueError('Nonempty bounded labelled predictions required.')
    ids=set();correct=abstentions=0
    for row in records:
        if not isinstance(row,dict) or set(row)!={'sample_id','expected_label','predicted_label','abstained'}:raise ValueError('Explicit labelled prediction contract required.')
        if not isinstance(row['sample_id'],str) or not 1<=len(row['sample_id'])<=80 or row['sample_id'] in ids:raise ValueError('Unique bounded sample identities required.')
        ids.add(row['sample_id'])
        if type(row['abstained']) is not bool or not isinstance(row['expected_label'],str) or not 1<=len(row['expected_label'])<=80:raise ValueError('Expected label and abstention required.')
        if row['abstained']:
            if row['predicted_label'] is not None:raise ValueError('Abstention cannot also assert a prediction.')
            abstentions+=1
        elif not isinstance(row['predicted_label'],str) or not 1<=len(row['predicted_label'])<=80:raise ValueError('Explicit prediction required.')
        else:correct+=row['predicted_label']==row['expected_label']
    with localcontext(Context(prec=40)) as context:
        context.prec=40
        accuracy=Decimal(correct)*100/len(records)
        return {'status':'SUPPLIED_PREDICTIONS_ONLY','samples':len(records),'correct':correct,'incorrect':len(records)-correct-abstentions,'abstentions':abstentions,'accuracy_percent':format(accuracy.quantize(Decimal('.0001')),'.4f'),'threshold_99_8_verified':False,'observed_accuracy_at_least_99_8':correct*1000>=len(records)*998,'model_executed':False,'professional_acceptance':False,'predicted_samples':len(records)-abstentions,'coverage_percent':format((Decimal(len(records)-abstentions)*100/len(records)).quantize(Decimal('.0001')),'.4f'),'accepted_accuracy_percent':format((Decimal(correct)*100/(len(records)-abstentions)).quantize(Decimal('.0001')),'.4f') if len(records)>abstentions else None}


def measure_attempt(observations, kind, operation, *, clock=None):
    """Retain failed-attempt latency without serializing input or exception text."""
    import time
    clock=clock or time.perf_counter_ns
    begin=clock()
    try:result=operation()
    except Exception:
        observations[kind].append({'duration_ns':clock()-begin,'ok':False})
        return False,None
    observations[kind].append({'duration_ns':clock()-begin,'ok':True})
    return True,result
