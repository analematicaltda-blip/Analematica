"""Prevent regression to anonymous, nonpersistent or fictitious legacy payment success."""
import unittest,sys,os,importlib,ast,json
from pathlib import Path
from unittest.mock import patch
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'BACKEND/SGA-CD-BACKEND'))
os.environ.setdefault('SECRET_KEY','synthetic-payment-boundary-only');os.environ.setdefault('DATABASE_URL','sqlite://')
from app.api.v1.endpoints import payments
from fastapi import HTTPException
class LegacyChecks(unittest.TestCase):
 def test_legacy_anonymous_checkout_never_calls_provider(self):
  body=payments.CheckoutRequest(plan_id='plan_estudiante',nombre_cliente='Synthetic',email_cliente='synthetic@example.test',telefono_cliente='3000000000')
  with patch.object(payments.payment_gateway,'generar_link_pago',side_effect=AssertionError('must not call provider')):
   with self.assertRaises(HTTPException) as e:payments.crear_checkout_pago(body)
  self.assertEqual(e.exception.status_code,409);self.assertEqual(e.exception.detail['code'],'PERSISTED_PAYMENT_INTENT_REQUIRED')
 def test_unstructured_agent_tools_no_longer_claim_financial_success(self):
  tree=ast.parse((root/'BACKEND/SGA-CD-BACKEND/app/tools/herramientas_crm_completo.py').read_text());names={'tool_'+n for n in ('generar_link_pago_online','verificar_webhook_pago','reintentar_cobro_fallido','actualizar_factura_pagada','enviar_comprobante_pago')};found=set()
  for node in ast.walk(tree):
   if isinstance(node,ast.FunctionDef) and node.name in names:
    returns=[n for n in ast.walk(node) if isinstance(n,ast.Return)];self.assertEqual(len(returns),1);value=json.loads(ast.literal_eval(returns[0].value));self.assertFalse(value['executed']);self.assertEqual(value['status'],'BLOCKED');found.add(node.name)
  self.assertEqual(found,names)
if __name__=='__main__':unittest.main()
