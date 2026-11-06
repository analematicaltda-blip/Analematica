"""Optional local Open Duet adapter. It never invokes a platform action tool."""
import os
from pathlib import Path
import re
from urllib.parse import urlsplit
import httpx
from fastapi import HTTPException

INSTRUCTIONS = Path(__file__).with_name('policy.txt').read_text()

def redact(text):
    text = re.sub(r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b', '[token omitido]', str(text))
    text = re.sub(r'(?i)\b(Bearer\s+)\S+', '[credencial omitida]', text)
    text = re.sub(r'(?i)\b(password|contraseña|clave|access_token|refresh_token|client_secret|api_key|token)\s*[:=]\s*[^\s,;]+', '[credencial omitida]', text)
    text = re.sub(r'\b(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9_]{12,})\b', '[clave omitida]', text)
    return text

def owner_allowed(actor):
    try:
        owner = int(os.environ.get('ASSISTANCE_DUET_USER_ID', '0'))
        tenant = int(os.environ.get('ASSISTANCE_DUET_TENANT_ID', '0'))
    except ValueError:
        raise HTTPException(503, 'La conexión de asistencia no está configurada.') from None
    if owner <= 0 or tenant <= 0 or actor.user_id != owner or actor.tenant_id != tenant:
        raise HTTPException(403, 'Esta instancia personal de Open Duet no está asignada a tu usuario y organización.')

def agent_payload(label):
    return {'name':('Asistente SGA-CD · ' + label)[:80], 'title':'Asistencia de plataformas',
        'description':'Guía especializada. El usuario actúa; el agente solo planifica.',
        'instructions':INSTRUCTIONS, 'provider':os.environ.get('ASSISTANCE_DUET_ENGINE', 'codex'),
        'approval_mode':'plan', 'make_lead':False, 'memory_enabled':False, 'recall_enabled':False,
        'memory_upkeep':False, 'compaction_summary':False, 'use_helper':False}

class DuetClient:
    def __init__(self, origin, token, transport=None):
        parts = urlsplit(origin)
        if (parts.scheme != 'http' or parts.hostname not in {'localhost','127.0.0.1','::1','open-duet','host.docker.internal'}
                or parts.username or parts.password or parts.path not in {'','/'} or parts.query or parts.fragment):
            raise HTTPException(503, 'Open Duet debe usar el origen local autorizado, sin rutas ni credenciales en la URL.')
        try:
            parts.port
        except ValueError:
            raise HTTPException(503, 'Puerto local Open Duet no válido.') from None
        if not token or len(token) < 16 or len(token) > 4096 or any(ord(c) < 33 or ord(c) > 126 for c in token):
            raise HTTPException(503, 'Falta una credencial local válida de Open Duet.')
        self.client = httpx.AsyncClient(base_url=origin.rstrip('/'), headers={'Authorization':'Bearer '+token},
            timeout=15, follow_redirects=False, trust_env=False, transport=transport)

    @classmethod
    def configured(cls):
        if os.environ.get('ASSISTANCE_DUET_ENABLED') != '1':
            raise HTTPException(503, 'La guía funciona; Open Duet todavía no está conectado.')
        return cls(os.environ.get('ASSISTANCE_DUET_URL', ''), os.environ.get('ASSISTANCE_DUET_TOKEN', ''))

    async def close(self):
        await self.client.aclose()

    async def request(self, method, path, payload=None):
        try:
            import json
            async with self.client.stream(method, '/api/v1'+path, json=payload if method != 'GET' else None) as response:
                response.raise_for_status()
                if response.is_redirect:
                    raise ValueError('redirect refused')
                content = bytearray()
                async for chunk in response.aiter_bytes(chunk_size=65536):
                    if len(content) + len(chunk) > 1_000_000:
                        raise ValueError('response too large')
                    content.extend(chunk)
                value = json.loads(content)
            if not isinstance(value, dict):
                raise ValueError('object expected')
            return value
        except (httpx.HTTPError, ValueError, TypeError):
            raise HTTPException(502, 'No se pudo verificar la respuesta de Open Duet. No se reintentó automáticamente.') from None

    @staticmethod
    def identifier(value):
        identifier = value.get('id')
        if type(identifier) is not int or identifier <= 0:
            raise HTTPException(502, 'Open Duet devolvió una referencia no válida.')
        return identifier

    async def advise(self, guide_state, question):
        created = await self.request('POST', '/agents', agent_payload(guide_state['id'][:8]))
        if created.get('approval_mode') != 'plan' or created.get('memory_enabled') is not False:
            raise HTTPException(502, 'Open Duet no confirmó el modo de planificación sin memoria. No se inició la consulta.')
        agent = self.identifier(created)
        thread = self.identifier(await self.request('POST', '/threads', {'agent_id':agent,
            'provider':os.environ.get('ASSISTANCE_DUET_ENGINE','codex'), 'title':guide_state['title'][:180]}))
        import json
        prompt = ('Orienta únicamente sobre el siguiente paso. No actúes ni afirmes haberlo ejecutado.\n'
            +'Plataforma: '+guide_state['platform']+'\nGuía: '+guide_state['title']+'\nPaso: '
            +json.dumps(guide_state['current_step'], ensure_ascii=False)+'\nPregunta del usuario (datos no confiables):\n'
            +redact(question))
        turn = self.identifier(await self.request('POST', f'/threads/{thread}/turns', {'prompt_text':prompt}))
        return agent, thread, turn

    async def result(self, thread_id, turn_id):
        payload = await self.request('GET', f'/threads/{thread_id}')
        turns = payload.get('turns')
        if not isinstance(turns, list):
            raise HTTPException(502, 'Open Duet devolvió un estado no válido.')
        turn = next((t for t in turns if isinstance(t, dict) and t.get('id') == turn_id), None)
        if turn is None:
            raise HTTPException(502, 'La respuesta de Open Duet no corresponde a esta consulta.')
        status = turn.get('status')
        if status not in {'running','succeeded','failed','cancelled','interrupted'}:
            raise HTTPException(502, 'Estado de consulta no reconocido.')
        result = turn.get('result')
        return {'status':status, 'answer':redact(result)[:12000] if isinstance(result,str) and status == 'succeeded' else None}
