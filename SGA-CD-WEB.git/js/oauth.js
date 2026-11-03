/* All clients use the same backend broker. No provider secret belongs in this file. */
document.addEventListener('DOMContentLoaded', async () => {
    const buttons = {google: document.getElementById('google-login-btn'), microsoft: document.getElementById('microsoft-login-btn')};
    const message = document.getElementById('login-mensaje');
    const api = config.apiBaseUrl.replace(/\/$/, '') + '/api/v1/sso';
    let busy = false;
    const show = text => { if (message) { message.textContent = text; message.setAttribute('role','status'); } };
    const pause = ms => new Promise(resolve => setTimeout(resolve,ms));
    for (const [provider, button] of Object.entries(buttons)) {
        if (!button) continue;
        button.disabled = true;
        button.textContent = provider === 'google' ? 'Continuar con Google' : 'Continuar con Microsoft (Outlook / Hotmail)';
        button.onclick = async () => {
            if (busy) return;
            const password = document.getElementById('password')?.value || '';
            if(!password) { show('Escribe tu contraseña de SGA-CD y continúa con el proveedor.'); return; }
            // Open synchronously to avoid popup blocking, then navigate to the broker.
            const popup = window.open('about:blank', '_blank');
            if (!popup) { show('Permite abrir la ventana de acceso e intenta de nuevo.'); return; }
            popup.opener = null;
            busy = true;
            try {
                const start = await fetch(api+'/'+provider+'/start', {method:'POST'});
                if (!start.ok) throw new Error('Este proveedor todavía no está configurado.');
                const flow = await start.json();
                popup.location.href = flow.authorization_url;
                show('Completa el acceso en la ventana de '+(provider==='google'?'Google.':'Microsoft.'));
                const expires = Date.now()+flow.expires_in*1000;
                while (Date.now()<expires) {
                    await pause(2500);
                    const response = await fetch(api+'/result', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({flow_id:flow.flow_id,proof:flow.proof,password})});
                    if (!response.ok) throw new Error('La cuenta no está autorizada o el acceso venció.');
                    const result = await response.json();
                    if (result.status !== 'authenticated') continue;
                    localStorage.setItem('accessToken',result.access_token);
                    localStorage.setItem('refreshToken',result.refresh_token);
                    localStorage.setItem('userRoles',JSON.stringify(result.user.roles));
                    localStorage.setItem('userId',String(result.user.id));
                    localStorage.setItem('userInquilinoId',String(result.user.inquilino_id));
                    localStorage.setItem('userName',result.user.nombre||'');
                    window.location.assign('app.html');
                    return;
                }
                throw new Error('El acceso venció. Intenta de nuevo.');
            } catch (error) { popup.close(); show(error.message || 'No se pudo completar el acceso.'); }
            finally { busy = false; }
        };
    }
    try {
        const response = await fetch(api+'/providers',{cache:'no-store'});
        if (!response.ok) throw new Error();
        const enabled = await response.json();
        for (const [provider,button] of Object.entries(buttons)) if(button) {
            button.disabled = enabled[provider] !== true;
            if(button.disabled) button.title = 'Pendiente de configurar por la administración';
        }
        if(!enabled.google && !enabled.microsoft) show('El acceso con Google y Microsoft aún no está habilitado. Puedes usar tu usuario y contraseña.');
    } catch { show('No se pudo consultar el acceso con proveedores. Puedes usar tu usuario y contraseña.'); }
});
