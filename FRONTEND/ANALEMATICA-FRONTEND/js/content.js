(() => {
  'use strict';
  const $ = id => document.getElementById(id), token = localStorage.getItem('accessToken');
  let selected = null, busy = false, dirty = false;
  const status = text => { $('status').textContent = text; };
  function controls() {
    $('save').disabled = busy || !token;
    $('generate').disabled = busy || !token;
    $('review').disabled = busy || dirty || !selected || selected.status !== 'draft';
    $('export').disabled = busy || dirty || !selected || selected.status !== 'reviewed';
    $('new').disabled = busy;
    for (const id of ['platform','brief','text','model','consent','checked']) $(id).disabled = busy;
  }
  async function api(path, body, method) {
    const response = await fetch('/api/v1/assistance/content' + path, {
      method: method || (body === undefined ? 'GET' : 'POST'),
      headers: { Authorization: 'Bearer ' + token, ...(body === undefined ? {} : {'Content-Type':'application/json'}) },
      body: body === undefined ? undefined : JSON.stringify(body), cache:'no-store', signal:AbortSignal.timeout(70000)
    });
    const data = await response.json();
    if (!response.ok) throw Error(typeof data.detail === 'string' ? data.detail : 'Revisa los datos y el acceso.');
    return data;
  }
  function show(data) {
    selected = data; dirty = false;
    $('platform').value = data.content.platform; $('brief').value = data.content.brief; $('text').value = data.content.text;
    $('version').textContent = `Versión ${data.revision} · ${data.status}`;
    $('source').textContent = JSON.stringify(data.source, null, 2);
    $('checked').checked = false; controls();
  }
  async function list() {
    const data = await api('/drafts'); $('drafts').replaceChildren();
    for (const row of data.drafts) {
      const item = document.createElement('li'), button = document.createElement('button');
      button.textContent = `${row.id.slice(0,8)} · ${row.status}`;
      button.onclick = () => run(async () => { show(await api('/drafts/' + row.id)); });
      item.append(button); $('drafts').append(item);
    }
  }
  async function run(action) {
    if (busy) return; busy = true; controls();
    try { await action(); } catch (error) { status(error.message); }
    finally { busy = false; controls(); }
  }
  const body = () => ({platform:$('platform').value, brief:$('brief').value, text:$('text').value});
  for (const id of ['platform','brief','text']) $(id).addEventListener('input', () => { dirty = true; $('checked').checked = false; controls(); });
  $('save').onclick = () => run(async () => {
    const data = selected ? await api('/drafts/' + selected.id, {...body(),revision:selected.revision}, 'PUT') : await api('/drafts',body());
    show(data); await list(); status('Borrador guardado. Revisa esta versión.');
  });
  $('generate').onclick = () => run(async () => {
    if (selected || $('text').value.trim()) throw Error('Abre un borrador nuevo y vacío antes de generar; conserva primero tus cambios.');
    show(await api('/generate', {platform:$('platform').value,brief:$('brief').value,model:$('model').value,share_with_local_model:$('consent').checked}));
    await list(); status('Borrador generado; su exactitud requiere revisión humana.');
  });
  $('review').onclick = () => run(async () => {
    show(await api('/drafts/' + selected.id + '/review', {revision:selected.revision,digest:selected.digest,accuracy_rights_privacy_checked:$('checked').checked}));
    await list(); status('Versión revisada. No se publicó contenido.');
  });
  $('export').onclick = () => run(async () => {
    const data = await api('/drafts/' + selected.id + '/export');
    const url = URL.createObjectURL(new Blob([JSON.stringify(data,null,2)], {type:'application/json'}));
    const link = document.createElement('a'); link.href = url; link.download = 'contenido-' + data.id + '.json'; link.click();
    setTimeout(() => URL.revokeObjectURL(url),1000); status('Contenido revisado exportado.');
  });
  $('new').onclick = () => { selected = null; dirty = false; $('brief').value = ''; $('text').value = ''; $('checked').checked = false; $('consent').checked = false; $('version').textContent = 'Nuevo borrador.'; $('source').textContent = ''; controls(); };
  controls(); if (token) run(async () => { await list(); status('Taller privado disponible.'); });
})();
