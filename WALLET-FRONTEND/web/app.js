'use strict';
const make=(tag,text,cls)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(cls)node.className=cls;return node;};
const state={pending:[]};
for(const button of document.querySelectorAll('[data-tab]'))button.addEventListener('click',()=>{
 for(const item of document.querySelectorAll('[data-tab]'))item.setAttribute('aria-selected',String(item===button));
 for(const panel of document.querySelectorAll('.panel'))panel.hidden=panel.id!==button.dataset.tab;
});
function renderPending(){
 const target=document.getElementById('pending');target.replaceChildren();const query=document.getElementById('search').value.toLocaleLowerCase('es');
 const filtered=state.pending.filter(item=>[item.id,item.area,item.title,item.acceptance].join(' ').toLocaleLowerCase('es').includes(query));
 for(const item of filtered){const card=make('article',undefined,'pending-item');card.append(make('span',item.id+' · '+item.status+' · '+item.owner,'pending-meta'),make('h3',item.title),make('p',item.acceptance));target.append(card);}
 document.getElementById('empty').hidden=filtered.length>0;
}
document.getElementById('search').addEventListener('input',renderPending);
Promise.all([fetch('team.json',{cache:'no-store'}),fetch('pending.json',{cache:'no-store'})]).then(async responses=>{
 if(responses.some(response=>!response.ok))throw Error();const [team,pending]=await Promise.all(responses.map(response=>response.json()));
 if(!Array.isArray(team)||team.length!==8||!Array.isArray(pending)||pending.some(item=>!item.id||!item.acceptance))throw Error();
 document.getElementById('team-count').textContent=String(team.length);document.getElementById('pending-count').textContent=String(pending.filter(item=>item.status!=='CERRADO').length);
 for(const agent of team){const card=make('article',undefined,'card');card.append(make('p','ASISTENCIA LOCAL','tag'),make('h3',agent.name),make('p',agent.task),make('p','Sin permiso para aprobar o ejecutar pagos.'));document.getElementById('team').append(card);}
 state.pending=pending.filter(item=>item.status!=='CERRADO');renderPending();
}).catch(()=>{document.getElementById('load-error').hidden=false;});
