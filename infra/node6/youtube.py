"""Upload only local reels, only as private videos, without automatic retries."""
import hashlib
import json
import os
import sqlite3
from urllib.parse import urlparse
import requests
from .engine import WorkerError

class YouTube:
    def __init__(self,engine,scope="operator"):self.engine=engine;self.scope=scope
    def upload(self,filename,title,description,made_for_kids):
        config=self.engine.config
        if not all([config.youtube_id,config.youtube_secret,config.youtube_refresh]):
            raise WorkerError('Autoriza primero tu canal de YouTube con youtube.upload; la clave de Gemini no autoriza publicaciones.')
        file=self.engine.artifact(filename)
        if file.suffix!='.mp4':raise WorkerError('Selecciona un reel MP4 del nodo',400)
        fingerprint=hashlib.sha256((('' if self.scope=='operator' else self.scope+'\0')+filename+json.dumps([title,description,made_for_kids])).encode()).hexdigest()
        database=config.output/'.youtube-jobs.sqlite3'
        with sqlite3.connect(database,timeout=10) as connection:
            database.chmod(0o600)
            connection.execute('CREATE TABLE IF NOT EXISTS uploads (fingerprint TEXT PRIMARY KEY,status TEXT,video_id TEXT)')
            connection.execute('BEGIN IMMEDIATE')
            previous=connection.execute('SELECT status,video_id FROM uploads WHERE fingerprint=?',(fingerprint,)).fetchone()
            if previous:
                if previous[0]=='uploaded':return {'status':'uploaded','privacy':'private','video_id':previous[1],'duplicate_prevented':True}
                raise WorkerError('Este envío ya se inició. Comprueba YouTube antes de intentar otro; no se repetirá automáticamente.',409)
            connection.execute('INSERT INTO uploads VALUES (?,?,NULL)',(fingerprint,'started'))
        client=self.engine.client
        try:
            token=client.post('https://oauth2.googleapis.com/token',data={'grant_type':'refresh_token','client_id':config.youtube_id,'client_secret':config.youtube_secret,'refresh_token':config.youtube_refresh},timeout=(10,30),allow_redirects=False)
            token.raise_for_status();access=token.json()['access_token']
            start=client.post('https://www.googleapis.com/upload/youtube/v3/videos',params={'uploadType':'resumable','part':'snippet,status'},headers={'Authorization':'Bearer '+access,'X-Upload-Content-Type':'video/mp4','X-Upload-Content-Length':str(file.stat().st_size)},json={'snippet':{'title':title,'description':description,'categoryId':'27'},'status':{'privacyStatus':'private','selfDeclaredMadeForKids':made_for_kids}},timeout=(10,30),allow_redirects=False)
            start.raise_for_status();location=start.headers['Location'];parsed=urlparse(location)
            if parsed.scheme!='https' or parsed.hostname!='www.googleapis.com' or parsed.username or parsed.port not in [None,443]:raise ValueError()
            with file.open('rb') as stream:
                response=client.put(location,headers={'Authorization':'Bearer '+access,'Content-Type':'video/mp4','Content-Length':str(file.stat().st_size)},data=stream,timeout=(10,180),allow_redirects=False)
            response.raise_for_status();result=response.json()
            video_id=result['id']
            if result.get('status',{}).get('privacyStatus')!='private':raise ValueError()
        except (requests.RequestException,ValueError,KeyError):
            raise WorkerError('No se pudo confirmar el envío privado. Revisa credenciales y tu canal antes de repetir; no hubo reintento automático.',502) from None
        with sqlite3.connect(database) as connection:connection.execute('UPDATE uploads SET status=?,video_id=? WHERE fingerprint=?',('uploaded',video_id,fingerprint))
        return {'status':'uploaded','privacy':'private','video_id':video_id,'url':'https://www.youtube.com/watch?v='+video_id}
