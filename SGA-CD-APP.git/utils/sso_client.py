"""Use the central broker in the browser; never store OAuth client secrets here."""
import asyncio
import os
import flet as ft
import requests


def begin_sso(page,provider,message,password):
    if not password:
        message.value='Escribe tu contraseña de SGA-CD y continúa con el proveedor.';page.update();return
    origin=os.getenv('SGACD_API_BASE_URL','').rstrip('/')
    if not origin:
        message.value='El acceso con proveedores todavía no está configurado.';page.update();return
    async def authorize():
        try:
            response=await asyncio.to_thread(requests.post,origin+'/api/v1/sso/'+provider+'/start',timeout=15)
            if not response.ok: raise ValueError('Este proveedor todavía no está configurado.')
            flow=response.json();page.launch_url(flow['authorization_url'])
            message.value='Completa el acceso en tu navegador y regresa aquí.';page.update()
            deadline=asyncio.get_running_loop().time()+flow['expires_in']
            while asyncio.get_running_loop().time()<deadline:
                await asyncio.sleep(3)
                response=await asyncio.to_thread(requests.post,origin+'/api/v1/sso/result',json={'flow_id':flow['flow_id'],'proof':flow['proof'],'password':password},timeout=15)
                if not response.ok: raise ValueError('Cuenta no autorizada o acceso vencido.')
                result=response.json()
                if result['status']!='authenticated':continue
                page.session.set('sso_session',result)
                page.go('/sso/account')
                return
            raise ValueError('El acceso venció. Intenta de nuevo.')
        except (requests.RequestException,ValueError,KeyError):
            message.value='No se completó el acceso. Comprueba la configuración y que tu correo esté autorizado.';page.update()
        finally:
            page.session.set('sso_pending',False)
    if not page.session.get('sso_pending'):
        page.session.set('sso_pending',True);page.run_task(authorize)


def account_view(page):
    """Show the verified central session separately from the legacy local database."""
    session=page.session.get('sso_session')
    if not session:return ft.View('/sso/account',[ft.Text('Inicia sesión para continuar.')])
    user=session['user']
    def logout(_):
        page.session.remove('sso_session');page.go('/login')
    return ft.View('/sso/account',[
        ft.Text('Sesión iniciada',size=28,weight=ft.FontWeight.BOLD),
        ft.Text(user.get('nombre') or user['email'],size=22),
        ft.Text(user['email']),ft.Text('Roles: '+', '.join(user['roles'])),
        ft.Text('Tu cuenta institucional se ha verificado correctamente.'),
        ft.ElevatedButton('Cerrar sesión',on_click=logout)
    ],spacing=16,padding=24,scroll=ft.ScrollMode.AUTO)
