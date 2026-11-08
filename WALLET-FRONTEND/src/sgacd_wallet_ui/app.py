"""Shared Flet interface. Web preview never unlocks a device's local secrets."""
import os
import asyncio
import time
import threading
from pathlib import Path
import flet as ft
from sgacd_wallet_offline import Workspace,WalletLocalError
from sgacd_wallet_offline.army import catalog,review_draft
from sgacd_wallet_offline.readiness import pending
LABELS={'DRAFT':'Borrador','REVIEWED_LOCALLY':'Primera revisión local','READY_FOR_SERVER_REVIEW':'Pendiente de revisión del servidor'}

class WalletApp:
    def __init__(self,page,mode='desktop',storage=None):
        self._session_lock=threading.Lock();self.session_epoch=0;self.foreground=True
        self.page=page;self.mode=mode;self.workspace=None;self.section='Resumen';self.message='';self.editing_id=None;self.edit_fields={}
        # A web session must never gain access to server-side files by presenting a passphrase.
        self.local_allowed=mode in {'mobile','desktop'} and not page.web
        forced_web=os.environ.get('FLET_FORCE_WEB_SERVER','').lower() in {'1','true','yes'}
        unsafe_bind=os.environ.get('FLET_SERVER_IP','') not in {'','127.0.0.1','localhost','::1','[::1]'}
        if forced_web or unsafe_bind:self.local_allowed=False
        self.screen_ready=mode!='mobile';self._alive=True;self.last_activity=time.monotonic();self.screen=None
        root=storage or os.environ.get('FLET_APP_STORAGE_DATA')
        if mode=='mobile' and self.local_allowed and not root:self.local_allowed=False
        desktop_root=Path(os.environ['LOCALAPPDATA'])/'AnalematicaWallet' if os.name=='nt' and os.environ.get('LOCALAPPDATA') else Path.home()/'.sgacd-wallet'
        self.path=Path(root or desktop_root)/'private-wallet'/'workspace.sqlite3'
        page.title='Billetera · Analemática';page.theme_mode=ft.ThemeMode.DARK;page.bgcolor='#060B17';page.theme=ft.Theme(color_scheme=ft.ColorScheme(primary='#7DD3FC',on_primary='#FFFFFF',surface='#0E1B38',on_surface='#FFFFFF',secondary='#38BDF8',on_secondary='#FFFFFF'),text_theme=ft.TextTheme(body_medium=ft.TextStyle(color='#FFFFFF'),body_large=ft.TextStyle(color='#FFFFFF'),title_large=ft.TextStyle(color='#FFFFFF')));page.padding=20;page.scroll=ft.ScrollMode.AUTO
        page.on_disconnect=self.disconnect
        page.on_app_lifecycle_state_change=self.lifecycle
        page.window.on_event=self.window_event
        if mode=='mobile' and self.local_allowed:
            try:
                from sgacd_vault import SensitiveDisplay
                self.screen=SensitiveDisplay();page.overlay.append(self.screen)
            except ImportError:self.local_allowed=False
        self.render()
        page.run_task(self.auto_lock)
    async def auto_lock(self):
        while self._alive:
            await asyncio.sleep(15)
            if self.workspace is not None and time.monotonic()-self.last_activity>=300:
                self.close();self.message='Espacio bloqueado por inactividad.';self.render()
    def disconnect(self,e):self._alive=False;self.close()
    def lifecycle(self,e):
        state=str(getattr(e,'state',getattr(e,'data',''))).lower()
        if any(value in state for value in ['inactive','paused','hidden','detached']):self.foreground=False;self.close();self.screen_ready=self.mode!='mobile';self.render()
        elif 'resumed' in state:self.foreground=True;self.render()
    def window_event(self,e):
        if getattr(e,'data','')=='close':self.disconnect(e);return
        if getattr(e,'data','') in {'blur','minimize','hide'}:self.foreground=False;self.close();self.render()
        elif getattr(e,'data','') in {'focus','restore'}:self.foreground=True;self.render()
    async def activate_screen(self,e):
        epoch=self.session_epoch
        try:
            await self.screen.protect()
            if epoch!=self.session_epoch or not self.foreground:raise WalletLocalError("SESSION_CHANGED")
            self.screen_ready=True;self.message='Protección local preparada.'
        except Exception:self.screen_ready=False;self.message='La protección de pantalla no está disponible; el espacio permanece bloqueado.'
        self.render()
    def close(self):
        with self._session_lock:
            workspace=self.workspace;self.workspace=None;self.session_epoch+=1
            self.editing_id=None;self.edit_fields={}
            for name in ['password','note_title','note_content','source','destination','amount','currency']:
                control=getattr(self,name,None)
                if control is not None:control.value=None
        if workspace:workspace.close()
    def banner(self):
        return ft.Container(content=ft.Text('Modo local: apuntes y borradores cifrados. Ninguna transferencia se ejecuta sin conexión. Las revisiones locales no sustituyen las autorizaciones del servidor.',color='#FFFFFF'),bgcolor='#142850',padding=16,border_radius=12)
    def action(self,callback):
        self.last_activity=time.monotonic()
        try:callback();self.message='Operación local completada.'
        except WalletLocalError as error:
            labels={'PASSPHRASE_12_128_REQUIRED':'Usa una contraseña de 12 a 128 caracteres.','UNLOCK_OR_INTEGRITY_FAILED':'No se pudo abrir el espacio. Revisa la contraseña o la integridad del archivo.','LOCAL_REVIEW_REJECTED':'La revisión cambió o venció. Edita el borrador y vuelve a revisarlo.','CONCURRENT_CHANGE_REOPEN_REQUIRED':'Otro proceso modificó el espacio. Bloquea y vuelve a abrirlo.'}
            self.message=labels.get(str(error),'No se pudo completar la operación local. Revisa los datos; el archivo no se reinició.')
        except Exception:self.message='La operación no se completó. No se habilitó ninguna transferencia.'
        self.render()
    def open_local(self,create=False):
        with self._session_lock:
            if not self.local_allowed or not self.screen_ready or not self.foreground or not self._alive:raise WalletLocalError("NATIVE_SCREEN_REQUIRED")
            epoch=self.session_epoch;passphrase=self.password.value or '';self.password.value=''
        workspace=Workspace.create(self.path,passphrase) if create else Workspace.unlock(self.path,passphrase)
        with self._session_lock:
            if epoch!=self.session_epoch or self.workspace is not None:
                workspace.close();raise WalletLocalError('SESSION_CHANGED')
            self.workspace=workspace
    def nav(self,name):self.section=name;self.message='';self.render()
    def render(self):
        if not self._alive:return
        body=[ft.Row([ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,color='#7DD3FC',size=32),ft.Text('Billetera',size=30,weight=ft.FontWeight.BOLD)],wrap=True),
              ft.Text('Tu trabajo local, protegido y bajo tu control.',color='#FFFFFF'),self.banner(),
              ft.Row([ft.OutlinedButton(name,on_click=lambda e,n=name:self.nav(n)) for name in ['Resumen','Borradores','Apuntes','Equipo','Producción']],wrap=True)]
        if self.message:body.append(ft.Text(self.message,color='#FFFFFF',selectable=True))
        if self.section=='Equipo':
            body.extend([ft.Text('Equipo de asistencia',size=22,weight=ft.FontWeight.BOLD),ft.Text('Ocho soldados de reglas locales. Open Duet y agent-desktop quedan sujetos a vinculación y al control de autorizaciones existente.')])
            for soldier in catalog():body.append(ft.Container(ft.Column([ft.Text(soldier['name'],weight=ft.FontWeight.BOLD),ft.Text(soldier['task'])]),bgcolor='#0E1B38',padding=14,border_radius=10))
        elif self.section=='Producción':
            body.extend([ft.Text('Validaciones pendientes',size=22,weight=ft.FontWeight.BOLD),ft.Text('Registro compartido de lo que aún impide habilitar operaciones reales.')])
            body.extend(ft.Container(ft.Column([ft.Text(item['id']+' · '+item['title'],weight=ft.FontWeight.BOLD),ft.Text(item['acceptance'])]),bgcolor='#0E1B38',padding=14,border_radius=10) for item in pending())
        elif not self.local_allowed:
            body.extend([ft.Text('Vista web de consulta',size=22,weight=ft.FontWeight.BOLD),ft.Text('Consulta el equipo y las validaciones. Para guardar apuntes cifrados utiliza la aplicación móvil o de escritorio en tu dispositivo. No introduzcas claves financieras en esta vista.')])
        elif not self.foreground:
            body.extend([ft.Text('Espacio bloqueado al salir'),ft.Text('Vuelve a la aplicación para abrir el espacio local.')])
        elif not self.screen_ready:
            body.extend([ft.Text('Preparar protección local',size=22,weight=ft.FontWeight.BOLD),ft.Text('Activa la protección de pantalla antes de introducir la contraseña o mostrar datos locales.'),ft.ElevatedButton('Activar protección local',on_click=self.activate_screen)])
        elif self.workspace is None:
            self.password=ft.TextField(label='Contraseña del espacio local',password=True,can_reveal_password=False,helper_text='Mínimo 12 caracteres. No es el PIN ni la llave de tu cuenta financiera.')
            body.extend([ft.Text('Espacio local bloqueado',size=22,weight=ft.FontWeight.BOLD),self.password,
                         ft.Row([ft.ElevatedButton('Abrir espacio',on_click=lambda e:self.action(lambda:self.open_local(False))),ft.OutlinedButton('Crear espacio nuevo',on_click=lambda e:self.action(lambda:self.open_local(True)))],wrap=True),
                         ft.Text('Crear no reemplaza un archivo existente. Se bloquea al salir y tras cinco minutos sin acciones; guarda tus cambios antes. Si pierdes la contraseña, el caché no se recupera automáticamente.')])
        else:
            try:state=self.workspace.snapshot()
            except (WalletLocalError,AttributeError):self.close();self.render();return
            body.append(ft.TextButton('Bloquear espacio',on_click=lambda e:self.action(self.close)))
            if self.section=='Resumen':
                body.extend([ft.Text('Espacio local abierto',size=22,weight=ft.FontWeight.BOLD),ft.Text(f"{len(state['drafts'])} borradores · {len(state['notes'])} apuntes"),ft.Text('No hay saldo bancario verificado en este modo.'),ft.Row([ft.ElevatedButton('Preparar borrador',on_click=lambda e:self.nav('Borradores')),ft.OutlinedButton('Registrar apunte',on_click=lambda e:self.nav('Apuntes'))],wrap=True)])
            elif self.section=='Apuntes':
                self.note_title=ft.TextField(label='Título');self.note_content=ft.TextField(label='Apunte',multiline=True,min_lines=3,max_length=2000)
                body.extend([ft.Text('Apuntes privados',size=22,weight=ft.FontWeight.BOLD),self.note_title,self.note_content,ft.ElevatedButton('Guardar apunte',on_click=lambda e:self.action(lambda:self.workspace.add_note(self.note_title.value or '',self.note_content.value or '')))])
                for note in reversed(state['notes']):body.append(ft.Container(ft.Column([ft.Text(note['title'],weight=ft.FontWeight.BOLD),ft.Text(note['content'],selectable=True)]),bgcolor='#0E1B38',padding=14,border_radius=10))
            elif self.section=='Borradores':
                self.source=ft.TextField(label='Cuenta de origen (identificador)',value=self.edit_fields.get('source',''));self.destination=ft.TextField(label='Cuenta de destino (identificador)',value=self.edit_fields.get('destination',''));self.amount=ft.TextField(label='Importe',value=self.edit_fields.get('amount',''));self.currency=ft.Dropdown(label='Moneda',value=self.edit_fields.get('currency'),options=[ft.dropdown.Option(value) for value in ['COP','USD','EUR']])
                body.extend([ft.Text('Preparar, sin enviar dinero',size=22,weight=ft.FontWeight.BOLD),self.source,self.destination,ft.Row([ft.Container(self.amount,expand=True),ft.Container(self.currency,expand=True)]),ft.ElevatedButton('Guardar cambios y reiniciar revisiones' if self.editing_id else 'Guardar borrador',on_click=lambda e:self.action(self.save_draft))])
                for draft in reversed(state['drafts']):
                    fields=draft['fields'];stage=len(draft['acks'])+1
                    controls=[ft.Text(fields['amount']+' '+fields['currency'],size=20,weight=ft.FontWeight.BOLD),ft.Text('Origen: '+fields['source']),ft.Text('Destino: '+fields['destination']),ft.Text(LABELS[draft['state']])]
                    if stage<=2:controls.append(ft.OutlinedButton(f'Confirmar revisión local {stage}/2',on_click=lambda e,d=draft,s=stage:self.action(lambda:self.workspace.acknowledge(d['id'],self.workspace.actor_id,d['digest'],s))))
                    else:controls.append(ft.Text('Esperará una intención nueva y dos autorizaciones de hardware en el servidor. No se envía automáticamente.'))
                    controls.append(ft.TextButton('Modificar borrador',on_click=lambda e,d=draft:self.edit_draft(d)))
                    controls.append(ft.TextButton('Consultar revisión de los soldados',on_click=lambda e,d=draft:self.show_review(d)))
                    body.append(ft.Container(ft.Column(controls),bgcolor='#0E1B38',padding=14,border_radius=10))
        self.page.controls.clear();self.page.add(ft.Column(body,spacing=16));self.page.update()
    def edit_draft(self,draft):
        self.editing_id=draft['id'];self.edit_fields=dict(draft['fields']);self.render()
    def save_draft(self):
        values=(self.source.value,self.destination.value,self.amount.value,self.currency.value)
        if self.editing_id:self.workspace.edit_draft(self.editing_id,*values)
        else:self.workspace.add_draft(*values)
        self.editing_id=None;self.edit_fields={}
    def show_review(self,draft):
        report=review_draft(draft,self.workspace.actor_id);self.message=f"{len(report['agents'])} soldados revisaron el borrador. El servidor y sus dos autorizaciones siguen pendientes. No se movieron fondos.";self.render()

def run(page,mode='desktop'):return WalletApp(page,mode)
