"""Check a real Flet session inside its container; needs no host dependencies."""
import json
import sys
import time
from urllib.request import urlopen
from websockets.sync.client import connect

port=int(sys.argv[1]); width=390 if port==8502 else 1280
with urlopen(f'http://127.0.0.1:{port}/',timeout=10) as response:
    assert response.status==200
    assert b'flutter_bootstrap.js' in response.read()
payload=dict(pageName='',pageRoute='/',pageWidth=str(width),pageHeight='900',
             windowWidth=str(width),windowHeight='900',windowTop='0',windowLeft='0',
             isPWA='false',isWeb='true',isDebug='false',platform='android' if port==8502 else 'windows',
             platformBrightness='dark',media='{}',sessionId='')
with connect(f'ws://127.0.0.1:{port}/ws',open_timeout=15,proxy=None) as ws:
    ws.send(json.dumps({'action':'registerWebClient','payload':payload}))
    deadline=time.monotonic()+25
    text=''
    while time.monotonic()<deadline:
        message=ws.recv(timeout=max(0.1,deadline-time.monotonic()))
        data=json.loads(message)
        response_payload=data.get('payload')
        if isinstance(response_payload,dict) and response_payload.get('error'):
            raise RuntimeError('Flet devolvió un error al iniciar la sesión')
        text+=message
        if any(label in text for label in ['Bienvenido al Sistema', 'Iniciar sesi', 'Iniciar Sesi']) and '38bdf8' in text.lower():
            print(f'OK {port}: HTTP 200, sesión WebSocket, vista inicial y paleta azul cielo')
            break
    else:
        raise RuntimeError('La sesión no generó la vista inicial esperada')
