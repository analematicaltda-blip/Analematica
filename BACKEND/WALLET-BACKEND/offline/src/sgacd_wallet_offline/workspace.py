"""Encrypted local notes/drafts; separate from nonexportable financial/device keys.
No account tokens, signed backend approvals or confirmed balances are persisted.
"""
import copy
from decimal import Decimal,InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import secrets
import sqlite3
import stat
import time
import threading
from functools import wraps
from uuid import UUID,uuid4
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class WalletLocalError(ValueError):pass
MAX_BYTES=1048576

def canonical_uuid(value):
    if not isinstance(value,str):raise WalletLocalError('INVALID_IDENTIFIER')
    try:parsed=UUID(value)
    except ValueError:raise WalletLocalError('INVALID_IDENTIFIER') from None
    if str(parsed)!=value:raise WalletLocalError('INVALID_IDENTIFIER')
    return value

def transfer_fields(source,destination,amount,currency):
    source=canonical_uuid(source);destination=canonical_uuid(destination)
    if source==destination or currency not in {'COP','USD','EUR'} or not isinstance(amount,str) or len(amount)>24:raise WalletLocalError('INVALID_DRAFT')
    try:
        value=Decimal(amount)
        if not value.is_finite() or value<=0 or value>=Decimal('10000000000000000') or value!=value.quantize(Decimal('.01')):raise InvalidOperation()
    except (InvalidOperation,ValueError):raise WalletLocalError('INVALID_AMOUNT') from None
    return {'source':source,'destination':destination,'amount':format(value,'.2f'),'currency':currency}

def digest(fields):return hashlib.sha256(json.dumps(fields,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def derive(passphrase,salt):
    if not isinstance(passphrase,str) or not 12<=len(passphrase)<=128:raise WalletLocalError('PASSPHRASE_12_128_REQUIRED')
    return bytearray(hashlib.pbkdf2_hmac('sha256',passphrase.encode(),b'SGACD-DRAFT-CACHE-V1'+salt,600000,32))

def serialized(function):
    @wraps(function)
    def guarded(self,*args,**kwargs):
        with self._lock:return function(self,*args,**kwargs)
    return guarded

class Workspace:
    def __init__(self,path):
        self._lock=threading.RLock();self.path=Path(path);self._db=None;self._key=None;self._state=None;self._generation=None;self._workspace=None
    def _connect(self):
        if self.path.is_symlink() or not self.path.is_file() or (os.name=='posix' and self.path.stat().st_mode&0o077):raise WalletLocalError('PRIVATE_WORKSPACE_REQUIRED')
        db=sqlite3.connect(self.path.resolve().as_uri()+'?mode=rw',uri=True,timeout=8,check_same_thread=False);db.execute('PRAGMA temp_store=MEMORY')
        return db
    @classmethod
    def create(cls,path,passphrase):
        obj=cls(path);parent=obj.path.parent
        if parent.is_symlink():raise WalletLocalError('PRIVATE_WORKSPACE_REQUIRED')
        parent.mkdir(mode=0o700,parents=True,exist_ok=True)
        if os.name=='posix' and stat.S_IMODE(parent.stat().st_mode)&0o077:raise WalletLocalError('PRIVATE_WORKSPACE_REQUIRED')
        salt=secrets.token_bytes(16);key=derive(passphrase,salt)
        try:
            descriptor=os.open(obj.path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0),0o600);os.close(descriptor)
        except OSError:raise WalletLocalError('WORKSPACE_EXISTS_OR_UNAVAILABLE') from None
        try:
            obj._db=obj._connect();obj._key=key;obj._workspace=str(uuid4());obj._generation=0
            obj._state={'schema':1,'local_actor':str(uuid4()),'notes':[],'drafts':[]}
            nonce=secrets.token_bytes(12);cipher=obj._seal(obj._state,nonce,0)
            with obj._db:
                obj._db.execute('CREATE TABLE vault (slot INTEGER PRIMARY KEY CHECK(slot=1), workspace TEXT NOT NULL, generation INTEGER NOT NULL, salt BLOB NOT NULL, nonce BLOB NOT NULL, cipher BLOB NOT NULL)')
                obj._db.execute('INSERT INTO vault VALUES(1,?,?,?,?,?)',(obj._workspace,0,salt,nonce,cipher))
            return obj
        except Exception:
            obj.close();raise WalletLocalError('WORKSPACE_CREATION_FAILED_NO_AUTOMATIC_RESET') from None
    @classmethod
    def unlock(cls,path,passphrase):
        obj=cls(path)
        try:
            obj._db=obj._connect()
            lengths=obj._db.execute('SELECT length(cipher),length(salt),length(nonce) FROM vault WHERE slot=1').fetchone()
            if not lengths or not 16<=lengths[0]<=MAX_BYTES or lengths[1:]!=(16,12):raise WalletLocalError('WORKSPACE_INTEGRITY_FAILED')
            workspace,generation,salt,nonce,cipher=obj._db.execute('SELECT workspace,generation,salt,nonce,cipher FROM vault WHERE slot=1').fetchone()
            obj._workspace=canonical_uuid(workspace)
            if type(generation)is not int or generation<0:raise WalletLocalError('WORKSPACE_INTEGRITY_FAILED')
            obj._generation=generation;obj._key=derive(passphrase,salt)
            state=json.loads(AESGCM(bytes(obj._key)).decrypt(nonce,cipher,obj._aad(generation)))
            if set(state)!={'schema','local_actor','notes','drafts'} or state['schema']!=1 or not isinstance(state['notes'],list) or not isinstance(state['drafts'],list):raise WalletLocalError('WORKSPACE_INTEGRITY_FAILED')
            canonical_uuid(state['local_actor']);obj._state=state;return obj
        except Exception:
            obj.close();raise WalletLocalError('UNLOCK_OR_INTEGRITY_FAILED') from None
    def _aad(self,generation):return f'SGACD-WALLET-DRAFT-V1/{self._workspace}/{generation}'.encode()
    def _seal(self,state,nonce,generation):
        raw=json.dumps(state,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
        if len(raw)>MAX_BYTES-16:raise WalletLocalError('WORKSPACE_LIMIT')
        return AESGCM(bytes(self._key)).encrypt(nonce,raw,self._aad(generation))
    def _require_open(self):
        if self._state is None or self._key is None:raise WalletLocalError('WORKSPACE_LOCKED')
    def _commit(self,state):
        self._require_open();nonce=secrets.token_bytes(12);next_generation=self._generation+1;cipher=self._seal(state,nonce,next_generation)
        try:
            with self._db:
                self._db.execute('BEGIN IMMEDIATE')
                count=self._db.execute('UPDATE vault SET generation=?,nonce=?,cipher=? WHERE slot=1 AND generation=?',(next_generation,nonce,cipher,self._generation)).rowcount
                if count!=1:raise WalletLocalError('CONCURRENT_CHANGE_REOPEN_REQUIRED')
        except WalletLocalError:raise
        except sqlite3.Error:raise WalletLocalError('LOCAL_WRITE_FAILED') from None
        self._state=state;self._generation=next_generation
    @property
    @serialized
    def actor_id(self):self._require_open();return self._state['local_actor']
    @serialized
    def snapshot(self):self._require_open();return copy.deepcopy(self._state)
    @serialized
    def add_note(self,title,content):
        self._require_open()
        if not isinstance(title,str) or not 1<=len(title.strip())<=80 or not isinstance(content,str) or not 1<=len(content.strip())<=2000:raise WalletLocalError('INVALID_NOTE')
        state=copy.deepcopy(self._state)
        if len(state['notes'])>=256:raise WalletLocalError('WORKSPACE_LIMIT')
        note={'id':str(uuid4()),'title':title.strip(),'content':content.strip(),'created_at':int(time.time())};state['notes'].append(note);self._commit(state);return note['id']
    @serialized
    def add_draft(self,source,destination,amount,currency):
        self._require_open();fields=transfer_fields(source,destination,amount,currency);state=copy.deepcopy(self._state)
        if len(state['drafts'])>=256:raise WalletLocalError('WORKSPACE_LIMIT')
        draft={'id':str(uuid4()),'fields':fields,'digest':digest(fields),'state':'DRAFT','acks':[],'expires_at':int(time.time())+900,'idempotency_key':str(uuid4())}
        state['drafts'].append(draft);self._commit(state);return draft['id']
    @serialized
    def edit_draft(self,draft_id,source,destination,amount,currency):
        self._require_open();state=copy.deepcopy(self._state);draft=self._find(state,draft_id)
        draft.update(fields=transfer_fields(source,destination,amount,currency),state='DRAFT',acks=[],expires_at=int(time.time())+900,idempotency_key=str(uuid4()))
        draft['digest']=digest(draft['fields']);self._commit(state)
    @staticmethod
    def _find(state,draft_id):
        canonical_uuid(draft_id)
        for draft in state['drafts']:
            if draft['id']==draft_id:return draft
        raise WalletLocalError('DRAFT_NOT_FOUND')
    @serialized
    def acknowledge(self,draft_id,actor_id,expected_digest,stage):
        """Two explicit LOCAL reviews only; not hardware proofs or payment authority."""
        self._require_open();state=copy.deepcopy(self._state);draft=self._find(state,draft_id)
        if actor_id!=self.actor_id or expected_digest!=draft['digest'] or digest(draft['fields'])!=expected_digest or draft['expires_at']<=int(time.time()) or type(stage)is not int or stage!=len(draft['acks'])+1 or stage not in {1,2}:raise WalletLocalError('LOCAL_REVIEW_REJECTED')
        draft['acks'].append({'stage':stage,'actor':actor_id,'digest':expected_digest});draft['state']='REVIEWED_LOCALLY' if stage==1 else 'READY_FOR_SERVER_REVIEW'
        self._commit(state)
    @serialized
    def server_review_payload(self,draft_id):
        """Returns ONLY a new prepare request. Never replays local acks as bank proofs."""
        self._require_open();draft=self._find(self._state,draft_id)
        if draft['state']!='READY_FOR_SERVER_REVIEW' or draft['expires_at']<=int(time.time()) or digest(draft['fields'])!=draft['digest']:raise WalletLocalError('FRESH_LOCAL_REVIEW_REQUIRED')
        return {**draft['fields'],'idempotency_key':draft['idempotency_key']}
    @serialized
    def close(self):
        if self._db is not None:self._db.close();self._db=None
        if self._key is not None:self._key[:]=bytes(len(self._key));self._key=None
        self._state=None;self._generation=None
