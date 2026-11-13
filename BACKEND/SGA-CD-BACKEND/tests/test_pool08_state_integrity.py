"""Canonical row/index bindings in real SQLAlchemy stores; disposable database only."""
import importlib
import runpy
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace

fixture = runpy.run_path(str(Path(__file__).with_name('test_pool08_crm.py')), run_name='state_integrity_fixture')
from app.commercial.pool08.crm import CRMError, digest

DOMAINS = [('pricing', 'CommercialPrice'), ('quotation', 'CommercialQuotation'), ('sales', 'CommercialSale')]
for domain, name in DOMAINS:
    importlib.import_module('app.commercial.pool08.' + domain + '_models')

class StateIntegrityChecks(unittest.TestCase):
    login = fixture['CRMChecks'].login
    def setUp(self):
        fixture['CRMChecks'].setUp(self)
        self.addCleanup(lambda: fixture['CRMChecks'].tearDown(self))
        self.base = SimpleNamespace(db=self.db, scope=str(uuid.uuid4()))

    def test_canonical_code_stays_reserved_when_index_is_corrupt(self):
        for domain, name in DOMAINS:
            model = getattr(importlib.import_module('app.commercial.pool08.' + domain + '_models'), name)
            store = importlib.import_module('app.commercial.pool08.' + domain + '_store').Store(self.base)
            ref = str(uuid.uuid4())
            document = dict(id=ref, revision=1, code='CODE-' + ref, status='DRAFT')
            row = model(id=ref, scope=self.base.scope, revision=1, code=document['code'], status='DRAFT', document=document, document_digest=digest(document))
            self.db.add(row)
            self.db.commit()
            for field, value in [('revision', 2), ('status', 'OTHER'), ('code', 'OTHER')]:
                setattr(row, field, value)
                self.db.commit()
                with self.assertRaises(CRMError) as error:
                    store.get(ref)
                self.assertEqual(error.exception.status, 503)
                if field == 'code':
                    with self.assertRaises(CRMError):
                        store.find_code(document['code'])
                setattr(row, field, document[field])
                self.db.commit()
            self.assertEqual(store.get(ref)['id'], ref)

    def test_valid_digest_cannot_rebind_document_to_other_id(self):
        domain, name = DOMAINS[0]
        model = getattr(importlib.import_module('app.commercial.pool08.' + domain + '_models'), name)
        ref = str(uuid.uuid4())
        document = dict(id=str(uuid.uuid4()), revision=1, code='BOUND', status='DRAFT')
        self.db.add(model(id=ref, scope=self.base.scope, revision=1, code='BOUND', status='DRAFT', document=document, document_digest=digest(document)))
        self.db.commit()
        store = importlib.import_module('app.commercial.pool08.pricing_store').Store(self.base)
        with self.assertRaises(CRMError) as error:
            store.get(ref)
        self.assertEqual(error.exception.status, 503)

if __name__ == '__main__':
    unittest.main()
