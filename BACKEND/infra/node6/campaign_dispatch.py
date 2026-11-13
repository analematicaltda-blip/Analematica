"""Durable per-company, per-job, per-phase idempotency across HTTP retries."""
import hashlib
import json
import sqlite3
import copy
import requests
from .engine import WorkerError
from .social import Social
from .youtube import YouTube
from dataclasses import replace
from .engine import Engine

def result(engine,scope,job_id,phase):
    path=engine.config.output/'.campaign-jobs.sqlite3'
    if not path.exists():return {'found':False}
    with sqlite3.connect(path,timeout=10) as db:
        row=db.execute('SELECT status,result FROM deliveries WHERE scope=? AND job_id=? AND phase=?',(scope,job_id,phase)).fetchone()
    if not row:return {'found':False}
    return {'found':True,'status':row[0],'result':json.loads(row[1]) if row[1] else None}

def dispatch(engine,body):
    payload=body.model_dump(exclude={'credentials','public_video_url','unsubscribe_url'})
    fingerprint=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    path=engine.config.output/'.campaign-jobs.sqlite3'
    with sqlite3.connect(path,timeout=10) as db:
        path.chmod(0o600)
        db.execute('CREATE TABLE IF NOT EXISTS deliveries (scope TEXT, job_id TEXT, phase INTEGER, fingerprint TEXT, status TEXT, result TEXT, PRIMARY KEY(scope,job_id,phase))')
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT fingerprint,status,result FROM deliveries WHERE scope=? AND job_id=? AND phase=?',(body.workspace,body.job_id,body.phase)).fetchone()
        if row:
            if row[0]!=fingerprint:raise WorkerError('El identificador de envío ya corresponde a otros datos.',409)
            if row[1]=='complete':return json.loads(row[2])
            return {'outcome':'unknown','detail':'Este envío ya está iniciado; requiere comprobación antes de repetir.'}
        db.execute('INSERT INTO deliveries VALUES (?,?,?,?,?,NULL)',(body.workspace,body.job_id,body.phase,fingerprint,'started'))
    credentials={key:value.get_secret_value() for key,value in body.credentials.items()}
    # Isolate cookies and mutable HTTP state between company deliveries.
    transport=requests.Session();isolated=copy.copy(engine);isolated.client=transport
    try:
        if body.provider=='youtube':
            config=replace(engine.config,youtube_id=credentials['client_id'],youtube_secret=credentials['client_secret'],youtube_refresh=credentials['refresh_token'])
            scoped=Engine(config);scoped.client=transport
            value=YouTube(scoped,body.workspace).upload(body.filename,body.title,body.description,body.options['made_for_kids'])
            value={'outcome':'published','remote_id':value['video_id'],'privacy':'private','provider_state':{}}
        else:value=Social(isolated).deliver(body.provider,body.filename,credentials,body.title,body.description,body.recipient,body.provider_state,body.options,body.public_video_url,body.unsubscribe_url)
    except WorkerError:
        value={'outcome':'rejected','detail':'La plataforma o el video no cumplen los requisitos para este envío. Revisa el canal y el formato.'}
    except Exception:
        # A process crash/unknown exception must never silently re-issue an external POST.
        value={'outcome':'unknown','detail':'No se pudo confirmar el envío; revisa la plataforma antes de repetir.'}
    finally:transport.close()
    with sqlite3.connect(path,timeout=10) as db:db.execute('UPDATE deliveries SET status=?,result=? WHERE scope=? AND job_id=? AND phase=?',('complete',json.dumps(value),body.workspace,body.job_id,body.phase))
    return value
