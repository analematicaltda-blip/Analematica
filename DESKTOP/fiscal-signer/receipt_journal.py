"""Explicit customer-host SQLite laboratory attempt journal; no network sender.

Records metadata/digests, never XML, credentials, private keys or fiscal acceptance.
The same document/profile/bytes retain one key across uncertain-outcome retries.
"""
from contextlib import contextmanager
from pathlib import Path
import hashlib,json,os,re,secrets,sqlite3
from receipt_validation import checked_profile,verify_receipt,STATES
from local_signer import LaboratorySigningError

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
def hex64(value):return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None

GUARDS={name:f"CREATE TRIGGER {name} BEFORE {operation} ON {table} BEGIN SELECT RAISE(ABORT,'append only'); END" for name,operation,table in [('no_intent_update','UPDATE','intent'),('no_intent_delete','DELETE','intent'),('no_event_update','UPDATE','event'),('no_event_delete','DELETE','event')]}

class ReceiptJournal:
    def __init__(self,path):
        self.path=Path(path)
        if not self.path.is_absolute() or any(p.is_symlink() for p in [self.path,*self.path.parents]):
            raise LaboratorySigningError('Explicit nonsymbolic local journal path required.')
        if self.path.parent.stat().st_mode&0o077:
            raise LaboratorySigningError('Private customer directory required.')

    @classmethod
    def initialize(cls,path):
        journal=cls(path)
        fd=os.open(journal.path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.close(fd)
        connection=sqlite3.connect(journal.path)
        try:
            connection.executescript('''
PRAGMA foreign_keys=ON;
CREATE TABLE intent(key TEXT PRIMARY KEY,company_id TEXT NOT NULL,document_id TEXT NOT NULL,profile_digest TEXT NOT NULL,signed_digest TEXT NOT NULL,UNIQUE(company_id,document_id));
CREATE TABLE event(intent_key TEXT NOT NULL REFERENCES intent(key),revision INTEGER NOT NULL,body TEXT NOT NULL,body_digest TEXT NOT NULL,previous_digest TEXT NOT NULL,PRIMARY KEY(intent_key,revision));
CREATE TRIGGER no_intent_update BEFORE UPDATE ON intent BEGIN SELECT RAISE(ABORT,'append only'); END;
CREATE TRIGGER no_intent_delete BEFORE DELETE ON intent BEGIN SELECT RAISE(ABORT,'append only'); END;
CREATE TRIGGER no_event_update BEFORE UPDATE ON event BEGIN SELECT RAISE(ABORT,'append only'); END;
CREATE TRIGGER no_event_delete BEFORE DELETE ON event BEGIN SELECT RAISE(ABORT,'append only'); END;
PRAGMA user_version=1;
''')
        finally:connection.close()
        return journal

    @contextmanager
    def transaction(self):
        if self.path.is_symlink() or not self.path.is_file() or self.path.stat().st_mode&0o077:
            raise LaboratorySigningError('Private existing customer journal required.')
        con=sqlite3.connect(self.path,timeout=5,isolation_level=None)
        try:
            con.execute('PRAGMA foreign_keys=ON');con.execute('PRAGMA synchronous=FULL')
            if con.execute('PRAGMA user_version').fetchone()[0]!=1 or dict(con.execute("SELECT name,sql FROM sqlite_master WHERE type='trigger'"))!=GUARDS:
                raise LaboratorySigningError('Journal schema/guards unavailable; no automatic repair.')
            con.execute('BEGIN IMMEDIATE')
            try:yield con
            except BaseException:con.execute('ROLLBACK');raise
            else:con.execute('COMMIT')
        finally:con.close()

    def identity(self,profile,signed_digest):
        profile=checked_profile(profile)
        if not hex64(signed_digest):raise LaboratorySigningError('Exact reviewed signed document digest required.')
        pin=digest(profile);key=digest([profile['company_id'],profile['document_id'],pin,signed_digest])
        return profile,(key,profile['company_id'],profile['document_id'],pin,signed_digest)

    def state(self,con,identity):
        row=con.execute('SELECT * FROM intent WHERE company_id=? AND document_id=?',identity[1:3]).fetchone()
        if row!=identity:raise LaboratorySigningError('One immutable profile and signed document per journal identity required.')
        rows=con.execute('SELECT revision,body,body_digest,previous_digest FROM event WHERE intent_key=? ORDER BY revision LIMIT 257',(identity[0],)).fetchall()
        if not rows or len(rows)>256:raise LaboratorySigningError('Bounded complete laboratory journal required.')
        state=None;token=None;previous=identity[0];response=None
        for index,(revision,raw,pin,parent) in enumerate(rows,1):
            body=json.loads(raw)
            if revision!=index or parent!=previous or digest([identity[0],revision,parent,body])!=pin:
                raise LaboratorySigningError('Journal chain changed.')
            if not isinstance(body,dict):raise LaboratorySigningError('Journal event must be a mapping.')
            keys=set(body);next_state=body.get('state')
            if index==1:
                valid=body=={'state':'PREPARED_LAB'}
            elif next_state=='IN_FLIGHT_LAB':
                valid=state in {'PREPARED_LAB','UNCERTAIN_LAB','PENDING_LAB_ONLY'} and keys=={'state','attempt_token'} and isinstance(body['attempt_token'],str) and re.fullmatch('[0-9a-f]{32}',body['attempt_token'])
            elif next_state=='UNCERTAIN_LAB':
                valid=state=='IN_FLIGHT_LAB' and keys=={'state','attempt_token'} and body['attempt_token']==token
            else:
                valid=next_state in set(STATES.values()) and state in {'IN_FLIGHT_LAB','UNCERTAIN_LAB','PENDING_LAB_ONLY'} and keys=={'state','attempt_token','response_sha256'} and body['attempt_token']==token and hex64(body['response_sha256'])
            if not valid:raise LaboratorySigningError('Invalid laboratory journal transition.')
            state=next_state;token=body.get('attempt_token',token);response=body.get('response_sha256',response);previous=pin
        return {'state':state,'attempt_token':token,'response_sha256':response,'revision':len(rows),'head_digest':previous}

    def append(self,con,identity,body,current=None):
        revision=1 if current is None else current['revision']+1
        if revision>256:raise LaboratorySigningError('Journal capacity reached; explicit reviewed archival required.')
        previous=identity[0] if current is None else current['head_digest'];pin=digest([identity[0],revision,previous,body])
        con.execute('INSERT INTO event VALUES(?,?,?,?,?)',(identity[0],revision,canonical(body),pin,previous))
        return self.state(con,identity)

    def public(self,identity,state,replayed=False):
        return {'schema':'sgacd-laboratory-transport-journal-v1','submission_key':identity[0],
            'company_id':identity[1],'document_id':identity[2],**state,'replayed':replayed,
            'mode':'LABORATORY_ONLY','network_called':False,'fiscal_accepted':False,
            'dian_origin_verified':False,'signed_document_bytes_verified':False,'ledger_written':False,'number_allocated':False,
            'usable_as_fiscal_acceptance':False}

    def prepare(self,*,profile,signed_document_sha256):
        _,identity=self.identity(profile,signed_document_sha256)
        with self.transaction() as con:
            exists=con.execute('SELECT 1 FROM intent WHERE company_id=? AND document_id=?',identity[1:3]).fetchone()
            if exists:return self.public(identity,self.state(con,identity),True)
            con.execute('INSERT INTO intent VALUES(?,?,?,?,?)',identity)
            state=self.append(con,identity,{'state':'PREPARED_LAB'})
            return self.public(identity,state)

    def inspect(self,*,profile,signed_document_sha256):
        _,identity=self.identity(profile,signed_document_sha256)
        with self.transaction() as con:return self.public(identity,self.state(con,identity))

    def begin_attempt(self,*,profile,signed_document_sha256):
        _,identity=self.identity(profile,signed_document_sha256)
        with self.transaction() as con:
            current=self.state(con,identity)
            if current['state'] not in {'PREPARED_LAB','UNCERTAIN_LAB','PENDING_LAB_ONLY'}:
                raise LaboratorySigningError('An in-flight or terminal laboratory attempt cannot be restarted.')
            state=self.append(con,identity,{'state':'IN_FLIGHT_LAB','attempt_token':secrets.token_hex(16)},current)
            return self.public(identity,state)

    def mark_uncertain(self,*,profile,signed_document_sha256,attempt_token):
        _,identity=self.identity(profile,signed_document_sha256)
        with self.transaction() as con:
            current=self.state(con,identity)
            if current['attempt_token']!=attempt_token or current['state'] not in {'IN_FLIGHT_LAB','UNCERTAIN_LAB'}:
                raise LaboratorySigningError('Current in-flight laboratory attempt required.')
            if current['state']=='UNCERTAIN_LAB':return self.public(identity,current,True)
            state=self.append(con,identity,{'state':'UNCERTAIN_LAB','attempt_token':attempt_token},current)
            return self.public(identity,state)

    def apply_receipt(self,*,profile,signed_document_sha256,attempt_token,raw,leaf_pem,root_pem):
        profile,identity=self.identity(profile,signed_document_sha256)
        # Verification occurs here, not in a caller-supplied success boolean.
        report=verify_receipt(raw,profile=profile,leaf_pem=leaf_pem,root_pem=root_pem)
        with self.transaction() as con:
            current=self.state(con,identity)
            if current['attempt_token']!=attempt_token:raise LaboratorySigningError('Stale laboratory attempt token.')
            if current['response_sha256']==report['response_sha256'] and current['state']==report['laboratory_response_state']:
                return self.public(identity,current,True)
            if current['state'] not in {'IN_FLIGHT_LAB','UNCERTAIN_LAB','PENDING_LAB_ONLY'}:
                raise LaboratorySigningError('Conflicting terminal response requires independent investigation.')
            state=self.append(con,identity,{'state':report['laboratory_response_state'],
                'attempt_token':attempt_token,'response_sha256':report['response_sha256']},current)
            return self.public(identity,state)
