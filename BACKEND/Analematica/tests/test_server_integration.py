#!/usr/bin/env python3
"""
Pruebas integrales de unión 100% de Backend y Frontend de Analemática.
Valida:
1. Servidor unificado entrega estáticos: /, /login.html, /admin.html, /agents/analematica_army.js.
2. Autenticación y sesión de dueño (/login, /session).
3. Configuración de landing (/config GET y PUT con revisión).
4. Radicación y lectura de prospectos (/inquiries).
5. Despacho y auditoría de órdenes de agentes tácticos (/commands).
6. Supervisión DIAN y Auditoría Global de Sistema.
"""

import unittest
import threading
import time
import json
import urllib.request
import urllib.parse
from pathlib import Path
from http.server import HTTPServer

import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from Analematica.backend.integrated_server import AnalematicaUnifiedHandler, run_server

TEST_PORT = 18090
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"

class AnalematicaServerIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(('127.0.0.1', TEST_PORT), AnalematicaUnifiedHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.3)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _get(self, path, token=None):
        url = BASE_URL + path
        req = urllib.request.Request(url, method='GET')
        if token:
            req.add_header('Authorization', f'Bearer {token}')
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
            content_type = resp.headers.get('Content-Type')
            return resp.status, data, content_type

    def _post(self, path, payload, token=None, as_form=False):
        url = BASE_URL + path
        if as_form:
            body = urllib.parse.urlencode(payload).encode('utf-8')
            ct = 'application/x-www-form-urlencoded'
        else:
            body = json.dumps(payload).encode('utf-8')
            ct = 'application/json'

        req = urllib.request.Request(url, data=body, method='POST')
        req.add_header('Content-Type', ct)
        if token:
            req.add_header('Authorization', f'Bearer {token}')

        with urllib.request.urlopen(req) as resp:
            data = resp.read()
            return resp.status, json.loads(data.decode('utf-8'))

    def _put(self, path, payload, token=None):
        url = BASE_URL + path
        body = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=body, method='PUT')
        req.add_header('Content-Type', 'application/json')
        if token:
            req.add_header('Authorization', f'Bearer {token}')

        with urllib.request.urlopen(req) as resp:
            data = resp.read()
            return resp.status, json.loads(data.decode('utf-8'))

    def test_01_static_landing_client_untouched(self):
        """Verifica que la landing del cliente se entregue HTTP 200 con su contenido íntegro."""
        status, data, ct = self._get('/')
        self.assertEqual(status, 200)
        self.assertIn('text/html', ct)
        text = data.decode('utf-8')
        self.assertIn('ANALEMÁTICA', text)
        self.assertIn('leadCaptureForm', text)

    def test_02_static_login_and_admin_pages(self):
        """Verifica la entrega de login.html, admin.html y el script militar analematica_army.js."""
        status_login, data_login, _ = self._get('/login.html')
        self.assertEqual(status_login, 200)
        self.assertIn('owner-login-form', data_login.decode('utf-8'))

        status_admin, data_admin, _ = self._get('/admin.html')
        self.assertEqual(status_admin, 200)
        admin_text = data_admin.decode('utf-8')
        self.assertIn('tab-agents', admin_text)
        self.assertIn('tab-supervision-dian', admin_text)
        self.assertIn('tab-system-audit', admin_text)

        status_army, data_army, ct_army = self._get('/agents/analematica_army.js')
        self.assertEqual(status_army, 200)
        self.assertIn('javascript', ct_army)
        self.assertIn('CoronelAnalematica', data_army.decode('utf-8'))

    def test_03_login_and_session_flow(self):
        """Verifica autenticación de dueño, emisión de token Bearer y comprobación de sesión."""
        # Login exitoso
        status, res = self._post('/api/v1/workspace/corporate/login', {'username': 'dueño', 'password': 'superpassword123'}, as_form=True)
        self.assertEqual(status, 200)
        self.assertIn('access_token', res)
        token = res['access_token']
        self.assertIn('owner', res['user']['roles'])

        # Comprobar sesión con token
        s_status, s_data, _ = self._get('/api/v1/workspace/corporate/session', token=token)
        self.assertEqual(s_status, 200)
        session_info = json.loads(s_data.decode('utf-8'))
        self.assertTrue(session_info['authenticated'])
        self.assertEqual(session_info['user']['id'], 1)

    def test_04_landing_config_get_and_put(self):
        """Verifica consulta y publicación con control de revisiones concurrentes."""
        status_login, res_login = self._post('/api/v1/workspace/corporate/login', {'username': 'owner', 'password': 'securepassword'}, as_form=True)
        token = res_login['access_token']

        # Consultar config
        status, data, _ = self._get('/api/v1/workspace/corporate/config')
        self.assertEqual(status, 200)
        current = json.loads(data.decode('utf-8'))
        self.assertIn('config', current)
        rev = current['revision']

        # Actualizar config
        cfg = current['config']
        cfg['header']['brand_tag'] = 'INGENIERÍA MODULAR INTEGRADA'
        p_status, p_res = self._put('/api/v1/workspace/corporate/config', {'config': cfg, 'revision': rev}, token=token)
        self.assertEqual(p_status, 200)
        self.assertEqual(p_res['status'], 'published')
        self.assertEqual(p_res['revision'], rev + 1)

    def test_05_inquiries_submission_and_retrieval(self):
        """Verifica radicación de prospectos de clientes y consulta protegida para administradores."""
        status_login, res_login = self._post('/api/v1/workspace/corporate/login', {'username': 'owner', 'password': 'securepassword'}, as_form=True)
        token = res_login['access_token']

        # Cliente envía diagnóstico
        lead_data = {
            "nombre": "Alcaldía Municipal de Prueba",
            "entidad": "Secretaría de Tecnologías",
            "correo": "contacto@alcaldia.gov.co",
            "telefono": "+57 310 9876543",
            "consent": True
        }
        status, res = self._post('/api/v1/workspace/corporate/inquiries', lead_data)
        self.assertEqual(status, 201)
        self.assertEqual(res['status'], 'success')

        # Dueño consulta bandeja
        l_status, l_data, _ = self._get('/api/v1/workspace/corporate/inquiries', token=token)
        self.assertEqual(l_status, 200)
        leads = json.loads(l_data.decode('utf-8'))['leads']
        self.assertTrue(any(l['nombre'] == "Alcaldía Municipal de Prueba" for l in leads))

    def test_06_tactical_agent_commands(self):
        """Verifica despacho de órdenes militares tácticas y comando de reversión undo."""
        status_login, res_login = self._post('/api/v1/workspace/corporate/login', {'username': 'owner', 'password': 'securepassword'}, as_form=True)
        token = res_login['access_token']

        # Orden de estado del sistema
        s_status, s_res = self._post('/api/v1/workspace/corporate/commands', {'command': 'Estado del sistema', 'target': 'analematica'}, token=token)
        self.assertEqual(s_status, 200)
        self.assertEqual(s_res['status'], 'read')
        self.assertIn('ONLINE', s_res['data']['status'])

        # Orden de cambio de visión
        c_status, c_res = self._post('/api/v1/workspace/corporate/commands', {'command': 'Modifica la visión de Analemática a: Líder iberoamericano 2031', 'target': 'analematica'}, token=token)
        self.assertEqual(c_status, 200)
        self.assertEqual(c_res['status'], 'executed')
        self.assertTrue(c_res['reversible'])

        # Orden de deshacer
        u_status, u_res = self._post('/api/v1/workspace/corporate/commands', {'command': 'Deshacer última orden', 'target': 'analematica'}, token=token)
        self.assertEqual(u_status, 200)
        self.assertEqual(u_res['operation'], 'undo')

    def test_07_dian_supervision_and_system_audit_apis(self):
        """Verifica los endpoints de supervisión DIAN y telemetría de auditoría."""
        status_login, res_login = self._post('/api/v1/workspace/corporate/login', {'username': 'owner', 'password': 'securepassword'}, as_form=True)
        token = res_login['access_token']

        # DIAN
        d_status, d_data, _ = self._get('/api/admin/plataforma/supervision-dian/', token=token)
        self.assertEqual(d_status, 200)
        dian = json.loads(d_data.decode('utf-8'))
        self.assertIn('resumen_ejecutivo', dian)
        self.assertIn('ultimas_facturas', dian)

        # Auditoría
        a_status, a_data, _ = self._get('/api/admin/plataforma/system-audit/', token=token)
        self.assertEqual(a_status, 200)
        audit = json.loads(a_data.decode('utf-8'))
        self.assertEqual(audit['estado_servidor'], 'OPTIMO')
        self.assertEqual(audit['rls_enforcement'], '100%_ACTIVE')

    def test_08_erp_five_divisions_command_routing(self):
        """Verifica el despacho y telemetría de las 5 grandes divisiones militares ERP."""
        status_login, res_login = self._post('/api/v1/workspace/corporate/login', {'username': 'owner', 'password': 'securepassword'}, as_form=True)
        token = res_login['access_token']

        erp_tests = [
            ("Calcular ratio de liquidez corriente", "FINANCIERO", "razon_corriente"),
            ("Reprogramar turnos del área técnica", "OPERATIVO", "insignia"),
            ("Lanzar campaña de reactivación por WhatsApp a prospectos calificados", "COMERCIAL", "leads_calificados"),
            ("Radicar expediente contable del mes", "ARCHIVO", "ultimo_hash_sha256"),
            ("Ejecutar balance de comprobación de sumas iguales", "CONTABLE", "sumas_iguales_cuadradas")
        ]

        for cmd, div, expected_telemetria_key in erp_tests:
            status, res = self._post('/api/v1/agent/command', {'command': cmd, 'target_division': div}, token=token)
            self.assertEqual(status, 200, f"Error despachando comando {cmd}")
            self.assertEqual(res['status'], 'executed')
            self.assertEqual(res['target_division'], div)
            self.assertIn('telemetria', res['data'])
            self.assertIn(expected_telemetria_key, res['data']['telemetria'])

    def test_09_admin_html_contains_all_five_erp_tabs(self):
        """Verifica que admin.html contenga los botones de navegación y panes de las 5 divisiones."""
        status, data, _ = self._get('/admin.html')
        self.assertEqual(status, 200)
        html = data.decode('utf-8')
        for tab_id in ['tab-financiero', 'tab-operativo', 'tab-comercial', 'tab-archivistica', 'tab-contable']:
            self.assertIn(f'data-tab="{tab_id}"', html)
            self.assertIn(f'id="{tab_id}"', html)

    def test_10_accounting_skills_integration(self):
        """Verifica la integración de Conta-Skills y skills-contabilidad en la división contable."""
        status_login, res_login = self._post('/api/v1/workspace/corporate/login', {'username': 'owner', 'password': 'securepassword'}, as_form=True)
        token = res_login['access_token']

        # Orden de cierre mensual y conciliación bancaria
        status, res = self._post('/api/v1/agent/command', {
            'command': 'Ejecutar cierre mensual y conciliación bancaria',
            'target_division': 'CONTABLE'
        }, token=token)
        self.assertEqual(status, 200)
        self.assertEqual(res['target_division'], 'CONTABLE')
        tel = res['data']['telemetria']
        self.assertIn('conciliacion_bancaria', tel)
        self.assertEqual(tel['conciliacion_bancaria']['estado'], 'CONCILIADO_EXACTO')
        self.assertIn('activos_fijos', tel)
        self.assertGreater(tel['activos_fijos']['depreciacion_mensual_cop'], 0)
        self.assertIn('cierre_checklist', tel)
        self.assertEqual(tel['cierre_checklist']['estado_conciliacion'], 'RECONCILED')

if __name__ == '__main__':
    unittest.main()
