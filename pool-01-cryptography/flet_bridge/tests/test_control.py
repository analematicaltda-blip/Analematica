import asyncio
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import AsyncMock
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from sgacd_vault import DocumentScope,DocumentVault,VaultError

class BridgeChecks(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.scope=DocumentScope(str(uuid4()),str(uuid4()))
        self.vault=DocumentVault(self.scope)
        self.invoke=AsyncMock();self.vault.invoke_method_async=self.invoke
    async def test_import_uses_only_opaque_metadata(self):
        document=str(uuid4())
        self.invoke.return_value=json.dumps({'ok':True,'protocol':1,'status':'stored','document_id':document})
        self.assertEqual((await self.vault.import_document())['document_id'],document)
        call=self.invoke.call_args
        self.assertEqual(call.args[0],'import_document')
        self.assertEqual(set(call.args[1]),{'tenant','account','version','hardware','request_id'})
        self.assertEqual(call.args[1]['tenant'],self.scope.tenant)
    async def test_provision_requires_explicit_consent(self):
        with self.assertRaises(VaultError):await self.vault.provision()
        self.invoke.assert_not_called()
        self.invoke.return_value=json.dumps({'ok':True,'protocol':1,'status':'provisioned'})
        self.assertEqual((await self.vault.provision(confirm_new_key=True))['status'],'provisioned')
    async def test_bytes_and_paths_cannot_be_arguments(self):
        for value in [b'private-document','file:///private/identity','https://attacker.test/doc',str(uuid4()).replace('-','')]:
            with self.subTest(value=type(value).__name__),self.assertRaises((TypeError,ValueError)):
                await self.vault.verify_document(value)
        self.invoke.assert_not_called()
    async def test_unknown_native_fields_are_rejected(self):
        self.invoke.return_value=json.dumps({'ok':True,'protocol':1,'status':'listed','documents':[],'has_more':False,'key':'private'})
        with self.assertRaisesRegex(VaultError,'INVALID_NATIVE_RESPONSE'):await self.vault.list_documents()
    async def test_verified_document_is_bound_to_requested_id(self):
        self.invoke.return_value=json.dumps({'ok':True,'protocol':1,'status':'verified','document_id':str(uuid4())})
        with self.assertRaisesRegex(VaultError,'SCOPE_MISMATCH'):await self.vault.verify_document(str(uuid4()))
    async def test_missing_native_plugin_has_no_fallback(self):
        self.invoke.side_effect=RuntimeError('private path or exception details')
        with self.assertRaisesRegex(VaultError,'^NATIVE_UNAVAILABLE$'):await self.vault.import_document()
    async def test_busy_operation_cannot_mix_scope_or_result(self):
        event=asyncio.Event()
        async def blocked(*args,**kwargs):
            await event.wait();return json.dumps({'ok':True,'protocol':1,'status':'listed','documents':[],'has_more':False})
        self.invoke.side_effect=blocked
        first=asyncio.create_task(self.vault.list_documents());await asyncio.sleep(0)
        with self.assertRaisesRegex(VaultError,'BUSY'):await self.vault.import_document()
        event.set();await first
    async def test_error_details_and_invalid_versions_are_not_trusted(self):
        for message in ['private path: /identity','PRIVATEDOCUMENTCONTENTS']:
            self.invoke.return_value=json.dumps({'ok':False,'code':message,'details':'private'})
            with self.assertRaisesRegex(VaultError,'^NATIVE_UNAVAILABLE$'):await self.vault.import_document()
        self.invoke.return_value=json.dumps({'ok':True,'protocol':True,'status':'listed','documents':[],'has_more':False})
        with self.assertRaisesRegex(VaultError,'INVALID_NATIVE_RESPONSE'):await self.vault.list_documents()
    async def test_invalid_scope_and_policy_are_rejected(self):
        for kwargs in [{'version':True},{'version':0},{'hardware':'SOFTWARE'}]:
            with self.assertRaises(ValueError):DocumentScope(self.scope.tenant,self.scope.account,**kwargs)
        with self.assertRaises(ValueError):DocumentScope('1-1-1-1-1',self.scope.account)
    async def test_integrity_block_is_visible_and_cannot_be_disabled_by_caller(self):
        self.invoke.return_value=json.dumps({'ok':False,'code':'CLIENT_INTEGRITY_BLOCKED'})
        with self.assertRaisesRegex(VaultError,'^CLIENT_INTEGRITY_BLOCKED$'):await self.vault.import_document()
        self.invoke.reset_mock()
        with self.assertRaises(TypeError):await self.vault.import_document(skip_integrity=True)
        self.invoke.assert_not_called()
    async def test_no_export_or_financial_method(self):
        for method in ['export_key','deposit','execute','decrypt']:
            with self.assertRaisesRegex(VaultError,'UNSUPPORTED_METHOD'):await self.vault._request(method)
        self.invoke.assert_not_called()

if __name__=='__main__':unittest.main()
