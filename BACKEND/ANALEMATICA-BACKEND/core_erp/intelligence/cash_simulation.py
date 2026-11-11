"""Bounded, seeded daily bootstrap scenarios; not a bank forecast or ledger write."""
import hashlib,json,random,sys
from datetime import date,timedelta
from decimal import Decimal,InvalidOperation,ROUND_HALF_UP,Context,localcontext
HORIZONS=(30,90,365)
VERSION='cash-bootstrap-v1'

from functools import wraps
def exact(function):
    @wraps(function)
    def wrapped(*args,**kwargs):
        with localcontext(Context(prec=64)):
            return function(*args,**kwargs)
    return wrapped


@exact
def cents(value):
    if isinstance(value,bool) or not isinstance(value,(str,int,Decimal)):
        raise ValueError('Money must be exact decimal text, integer or Decimal; floats are rejected.')
    if isinstance(value,str) and len(value)>64:raise ValueError('Money representation is too long.')
    try:amount=Decimal(value)
    except (InvalidOperation,ValueError):raise ValueError('Invalid money.') from None
    if not amount.is_finite() or amount.copy_abs()>Decimal('999999999999.99'):
        raise ValueError('Money outside the supported range.')
    if amount!=amount.quantize(Decimal('0.01')):raise ValueError('Money requires exact cents.')
    return int(amount*100)


@exact
def money(value):return format((Decimal(value)/100).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP),'.2f')


@exact
def simulate(parameters):
    required={'opening_cash','observations','seed','paths'}
    if not isinstance(parameters,dict) or set(parameters)!=required:raise ValueError('Explicit opening cash, observations, seed and paths are required.')
    opening=cents(parameters['opening_cash'])
    if opening<0:raise ValueError('Opening cash must be nonnegative.')
    seed=parameters['seed'];paths=parameters['paths']
    if type(seed) is not int or not 0<=seed<=4294967295:raise ValueError('Seed must be an unsigned 32-bit integer.')
    if type(paths) is not int or not 100<=paths<=2000:raise ValueError('Paths must be between 100 and 2000.')
    observations=parameters['observations']
    if not isinstance(observations,list) or not 7<=len(observations)<=366:raise ValueError('Provide 7 to 366 consecutive daily observations, including zero days.')
    values=[];dates=[]
    for observation in observations:
        if not isinstance(observation,dict) or set(observation)!={'date','net_cash_flow'}:raise ValueError('Each observation needs date and net cash flow.')
        try:
            if not isinstance(observation['date'],str):raise ValueError()
            day=date.fromisoformat(observation['date'])
            if day.isoformat()!=observation['date']:raise ValueError()
        except (ValueError,TypeError):raise ValueError('Use canonical ISO economic dates.') from None
        if dates and day-dates[-1]!=timedelta(days=1):raise ValueError('Daily observations must be ordered, unique and consecutive.')
        dates.append(day);values.append(cents(observation['net_cash_flow']))
    try:forecast_end=(dates[-1]+timedelta(days=365)).isoformat()
    except OverflowError:raise ValueError('The forecast exceeds the date range.') from None
    normalized={'opening_cents':opening,'observations':[{'date':d.isoformat(),'net_cents':v} for d,v in zip(dates,values)],'seed':seed,'paths':paths,'version':VERSION}
    digest=hashlib.sha256(json.dumps(normalized,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    rng=random.Random(seed);terminal={h:[] for h in HORIZONS};deficits={h:0 for h in HORIZONS}
    for _ in range(paths):
        cash=opening;negative=False
        for day in range(1,366):
            cash+=values[rng.randrange(len(values))];negative=negative or cash<0
            if day in terminal:
                terminal[day].append(cash);deficits[day]+=int(negative)
    results=[]
    for horizon in HORIZONS:
        ordered=sorted(terminal[horizon])
        def percentile(percent):return money(ordered[(percent*paths+99)//100-1])
        results.append({'days':horizon,'end_date':(dates[-1]+timedelta(days=horizon)).isoformat(),
            'ending_cash_p05':percentile(5),'ending_cash_p50':percentile(50),'ending_cash_p95':percentile(95),
            'ending_cash_mean':money(Decimal(sum(ordered))/paths),
            'paths_with_negative_cash':deficits[horizon],
            'negative_cash_path_fraction':format(Decimal(deficits[horizon])/paths,'.6f')})
    return {'model_version':VERSION,'runtime_python':f'{sys.version_info.major}.{sys.version_info.minor}',
        'source':'operator_declared_scenario_not_ledger','input_digest':digest,'seed':seed,'paths':paths,
        'observation_start':dates[0].isoformat(),'observation_end':dates[-1].isoformat(),'observation_count':len(values),
        'forecast_end':forecast_end,'opening_cash':money(opening),'results':results,
        'assumptions':['IID daily sampling with replacement; includes zero days explicitly',
                       'No automatic seasonality, FX, tax, payroll or debt model',
                       'Opening cash and observations are operator declarations, not independently verified'],
        'interval_interpretation':'empirical scenario percentiles, not calibrated confidence intervals',
        'production_qualified':False,'financial_execution':False,'ledger_written':False}


@exact
def backtest(parameters):
    """One chronological holdout of 365 days; outcomes never enter training or RNG."""
    if not isinstance(parameters,dict) or set(parameters)!={'scenario','actuals'}:
        raise ValueError('Explicit training scenario and separate held-out actuals are required.')
    actuals=parameters['actuals']
    if not isinstance(actuals,list) or len(actuals)!=365:
        raise ValueError('Provide exactly 365 subsequent held-out daily outcomes, including zero days.')
    dates=[];flows=[]
    for row in actuals:
        if not isinstance(row,dict) or set(row)!={'date','net_cash_flow'}:
            raise ValueError('Each outcome needs date and net cash flow.')
        try:
            if not isinstance(row['date'],str):raise ValueError()
            day=date.fromisoformat(row['date'])
            if day.isoformat()!=row['date']:raise ValueError()
        except (ValueError,TypeError):raise ValueError('Use canonical ISO outcome dates.') from None
        if dates and day-dates[-1]!=timedelta(days=1):raise ValueError('Held-out outcomes must be ordered and consecutive.')
        dates.append(day);flows.append(cents(row['net_cash_flow']))
    forecast=simulate(parameters['scenario'])
    if dates[0]-date.fromisoformat(forecast['observation_end'])!=timedelta(days=1):
        raise ValueError('Held-out data must begin immediately after training; overlap or gaps are rejected.')
    cash=int(Decimal(forecast['opening_cash'])*100);negative=False;observed={}
    for index,flow in enumerate(flows,1):
        cash+=flow;negative=negative or cash<0
        if index in HORIZONS:observed[index]=(cash,negative)
    evaluations=[];absolute_errors=[]
    for scenario in forecast['results']:
        cash,negative=observed[scenario['days']]
        predicted=int(Decimal(scenario['ending_cash_p50'])*100)
        low=int(Decimal(scenario['ending_cash_p05'])*100);high=int(Decimal(scenario['ending_cash_p95'])*100)
        error=cash-predicted;absolute_errors.append(abs(error))
        evaluations.append({'days':scenario['days'],'actual_ending_cash':money(cash),
            'predicted_ending_cash_p50':scenario['ending_cash_p50'],
            'actual_minus_predicted':money(error),'absolute_terminal_error':money(abs(error)),
            'empirical_interval_contains_actual':low<=cash<=high,
            'realized_path_ever_negative':negative,
            'scenario_negative_cash_fraction':scenario['negative_cash_path_fraction']})
    outcome_digest=hashlib.sha256(json.dumps([{'date':d.isoformat(),'net_cents':v} for d,v in zip(dates,flows)],sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'method':'single_chronological_holdout_v1','forecast':forecast,
        'holdout_start':dates[0].isoformat(),'holdout_end':dates[-1].isoformat(),'holdout_count':365,
        'outcome_digest':outcome_digest,'evaluations':evaluations,
        'mean_absolute_terminal_error_across_horizons':money(Decimal(sum(absolute_errors))/len(absolute_errors)),
        'interpretation':'One operator-declared holdout; horizons are correlated. Not calibrated coverage or verified bank outcomes.',
        'production_qualified':False,'financial_execution':False,'ledger_written':False}


@exact
def sensitivity(parameters):
    """Paired scenarios with common draws; explicit additive monetary shocks only."""
    if not isinstance(parameters,dict) or set(parameters)!={'scenario','shocks'}:
        raise ValueError('An explicit base scenario and bounded shocks are required.')
    shocks=parameters['shocks']
    if not isinstance(shocks,list) or not 1<=len(shocks)<=4:
        raise ValueError('Provide one to four named sensitivity shocks.')
    names=set();normalized=[]
    for shock in shocks:
        if not isinstance(shock,dict) or set(shock)!={'name','opening_cash_delta','daily_net_flow_delta'}:
            raise ValueError('Each shock needs name, opening-cash delta and daily-net-flow delta.')
        name=shock['name']
        if not isinstance(name,str) or not 1<=len(name.strip())<=80 or name.strip() in names:
            raise ValueError('Shock names must be bounded, nonempty and unique.')
        names.add(name.strip())
        normalized.append((name.strip(),cents(shock['opening_cash_delta']),cents(shock['daily_net_flow_delta'])))
    base=simulate(parameters['scenario']);variants=[]
    for name,opening_delta,daily_delta in normalized:
        # New containers: never mutate training, seed, observations or the caller's scenario.
        scenario={'opening_cash':money(cents(parameters['scenario']['opening_cash'])+opening_delta),
                  'seed':parameters['scenario']['seed'],'paths':parameters['scenario']['paths'],
                  'observations':[{'date':row['date'],'net_cash_flow':money(cents(row['net_cash_flow'])+daily_delta)}
                                  for row in parameters['scenario']['observations']]}
        simulated=simulate(scenario)
        changes=[]
        for prior,changed in zip(base['results'],simulated['results']):
            delta=int(Decimal(changed['ending_cash_p50'])*100)-int(Decimal(prior['ending_cash_p50'])*100)
            changes.append({'days':prior['days'],'ending_cash_p50_delta':money(delta),
                'negative_cash_fraction_delta':format(Decimal(changed['negative_cash_path_fraction'])-Decimal(prior['negative_cash_path_fraction']),'.6f')})
        variants.append({'name':name,'opening_cash_delta':money(opening_delta),'daily_net_flow_delta':money(daily_delta),
                         'simulation':simulated,'changes_from_base':changes})
    return {'method':'paired_additive_sensitivity_v1','base':base,'variants':variants,
            'comparison':'Same seed, sample count and ordered training dates; common resampling draws.',
            'interpretation':'Declared monetary shocks, not inferred elasticities, tax rules or investment advice.',
            'production_qualified':False,'financial_execution':False,'ledger_written':False}


@exact
def backtest_windows(parameters):
    """Chronologically ordered holdouts; descriptive summaries never assume independence."""
    if not isinstance(parameters,dict) or set(parameters)!={'windows'}:
        raise ValueError('Explicit chronological windows are required.')
    windows=parameters['windows']
    if not isinstance(windows,list) or not 2<=len(windows)<=4:
        raise ValueError('Provide two to four chronological backtesting windows.')
    evaluations=[];previous_origin=None;previous_end=None;overlapping=False
    for window in windows:
        result=backtest(window)
        origin=result['forecast']['observation_end']
        if previous_origin is not None and origin<=previous_origin:
            raise ValueError('Window forecast origins must be distinct and strictly increasing.')
        if previous_end is not None and result['holdout_start']<=previous_end:overlapping=True
        previous_origin=origin;previous_end=result['holdout_end'];evaluations.append(result)
    summary=[]
    for index,horizon in enumerate(HORIZONS):
        rows=[window['evaluations'][index] for window in evaluations]
        error=sum((Decimal(row['absolute_terminal_error']) for row in rows),Decimal('0.00'))/len(rows)
        covered=sum(int(row['empirical_interval_contains_actual']) for row in rows)
        summary.append({'days':horizon,'windows':len(rows),'mean_absolute_terminal_error':format(error.quantize(Decimal('0.01'),rounding=ROUND_HALF_UP),'.2f'),
                        'interval_contains_actual_count':covered,'interval_contains_actual_fraction':format(Decimal(covered)/len(rows),'.6f')})
    return {'method':'chronological_multi_holdout_v1','windows':evaluations,'summary':summary,
        'overlapping_holdouts':overlapping,'source':'operator_declared_windows_not_verified_bank_data',
        'interpretation':'Descriptive window aggregates; overlapping holdouts and correlated horizons are not independent samples or calibrated coverage.',
        'production_qualified':False,'financial_execution':False,'ledger_written':False}
