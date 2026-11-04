"""Owner command console: explicit operations, atomic content writes, audit and guarded undo.
No arbitrary shell/SQL, fabricated agent reports, external sends or model calls.
"""
import copy,hashlib,json,re,unicodedata,uuid
from urllib.parse import urlsplit
from sqlalchemy import update,func,text
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models.corporate import CorporatePage,CorporateCommand,CorporateOwner
from app.models.workspace import WorkspaceLead
from app.models.tenancy import Inquilino
from app.models.user import Usuario
from app.models.catalog import CatalogoEspecialidad
from app.models.academic import Inscripcion
from app.services.workspace_service import roles_of
from app.crud.settings import models as settings_models
Setting=settings_models.Setting
FIELDS={'titulo':'landing_hero_title','subtitulo':'landing_hero_subtitle','video':'landing_hero_video_url','logo':'landing_logo_url','carrusel':'landing_carousel_urls','correo':'landing_contact_email','pie de pagina':'landing_footer_copy','titulo seo':'landing_seo_title','descripcion seo':'landing_seo_description','pregunta 1':'landing_faq1_question','respuesta 1':'landing_faq1_answer','pregunta 2':'landing_faq2_question','respuesta 2':'landing_faq2_answer'}
ANALE_FIELDS={'titulo':'hero.title','subtitulo':'hero.subtitle','mision':'mision.text','vision':'vision.text','marca':'header.brand_name','lema':'header.brand_tag','contacto':'contacto.desc','pie de pagina':'footer.copyright'}
READS={'historial de ordenes':'history','ayuda':'help','mostrar ayuda':'help','estado del sistema':'status','estado sistema':'status','listar empresas':'companies','mostrar empresas':'companies','listar usuarios':'users','mostrar usuarios':'users','resumen crm':'crm','resumen del crm':'crm','resumen catalogo':'catalog','consultar landing sga cd':'landing','mostrar landing sga cd':'landing'}
def normalized(value):return ' '.join(''.join(c for c in unicodedata.normalize('NFKD',value.lower().replace('-',' ')) if not unicodedata.combining(c)).split())
def public_result(row):return json.loads(row.result)
def read(db,action,actor):
    if action=='help':return {'ordenes':['Estado del sistema','Historial de órdenes','Listar empresas','Listar usuarios','Resumen CRM','Resumen catálogo','Consultar landing SGA-CD','Cambia el título de SGA-CD a: Nuevo título','Cambia el video de SGA-CD a: https://…','Cambia el carrusel de SGA-CD a: https://…/foto1.jpg, https://…/foto2.jpg','Cambia la misión de Analemática a: Nuestra misión','Deshacer <identificador de orden>'],'campos_sga':list(FIELDS),'campos_analematica':list(ANALE_FIELDS),'alcance':'Contenido publicado y consultas administrativas conectadas. Las operaciones no registradas se rechazan sin simular éxito.'}
    if action=='history':return {'ordenes':[{'id':r.id,'destino':r.target,'operacion':r.operation,'estado':r.status,'deshecha':bool(r.undone_by),'fecha':r.created_at.isoformat() if r.created_at else None} for r in db.query(CorporateCommand).filter_by(actor_id=actor.user.id).order_by(CorporateCommand.created_at.desc()).limit(100)]}
    if action=='status':
        db.execute(text('SELECT 1'))
        return {'base_de_datos':'conectada','empresas':db.query(Inquilino).count(),'usuarios_activos':db.query(Usuario).filter_by(activo=True).count(),'inscripciones':db.query(Inscripcion).count(),'consola':'Analemática','nota':'Lectura de base de datos; no acredita la disponibilidad de proveedores externos.'}
    if action=='companies':return {'total':db.query(Inquilino).count(),'empresas':[{'id':r.id,'nombre':r.nombre_empresa,'plan':r.plan,'activa':r.activo} for r in db.query(Inquilino).order_by(Inquilino.id).limit(100)],'limite':100}
    if action=='users':return {'total':db.query(Usuario).count(),'usuarios':[{'id':r.id,'nombre':r.nombre_completo or r.nombre_usuario,'roles':sorted(roles_of(r)),'empresa_id':r.inquilino_id,'activo':r.activo} for r in db.query(Usuario).order_by(Usuario.id).limit(100)],'limite':100}
    if action=='crm':return {'contactos_plataforma':db.query(WorkspaceLead).filter_by(scope='platform').count(),'por_etapa':{stage:count for stage,count in db.query(WorkspaceLead.stage,func.count()).filter_by(scope='platform').group_by(WorkspaceLead.stage)}}
    if action=='catalog':return {'deportes':db.query(CatalogoEspecialidad).filter_by(es_estandar=True,vertical='deporte',activo=True).count(),'modalidades_culturales':db.query(CatalogoEspecialidad).filter_by(es_estandar=True,vertical='cultura',activo=True).count()}
    if action=='landing':return {alias:(db.get(Setting,key).value if db.get(Setting,key) else None) for alias,key in FIELDS.items()}
    raise HTTPException(422,'Consulta no registrada.')
def resolve_change(command,target):
    match=re.match(r'(?is)^\s*(?:cambia|cambiar|actualiza|actualizar|modifica|modificar|establece|establecer)\s+(.*?)\s+(?:a|por)\s*:\s*(.+?)\s*$',command)
    if not match:match=re.match(r'(?is)^\s*(?:cambia|actualiza|modifica|establece)\s+(.*?)\s*:\s*(.+?)\s*$',command)
    if not match:match=re.match(r'(?is)^\s*(?:cambia|cambiar|actualiza|actualizar|modifica|modificar|establece|establecer)\s+(.*?)\s+(?:a|por)\s+(.+?)\s*$',command)
    if not match:raise HTTPException(422,'Orden no conectada. Escribe Ayuda o usa: Cambia el título de SGA-CD a: Nuevo título. No se ejecutó ninguna acción.')
    label,value=match.groups();label=normalized(label)
    if 'analematica' in label:target='analematica'
    elif 'sga cd' in label or re.search(r'\bsga\b',label):target='sga'
    label=re.sub(r'\b(?:de|del|en|la|el|landing|pagina|principal|hero|sga cd|sga|analematica)\b',' ',label);label=' '.join(label.split())
    field=(FIELDS if target=='sga' else ANALE_FIELDS).get(label)
    if not field:raise HTTPException(422,'Campo no conectado para este destino. Consulta Ayuda; no se modificó contenido.')
    value=value.strip().strip('“”')
    if not value or len(value)>3000:raise HTTPException(422,'El valor debe contener entre 1 y 3000 caracteres.')
    if target=='sga':
        if label in ['video','logo','carrusel']:
            urls=[u.strip() for u in value.split(',')] if label=='carrusel' else [value]
            if len(urls)>20:raise HTTPException(422,'El carrusel admite hasta 20 imágenes por orden.')
            for url in urls:
                parsed=urlsplit(url)
                if any(ord(c)<32 for c in url) or '\\' in url or url.startswith('//') or not (parsed.scheme in ['https','http'] and parsed.netloc or not parsed.scheme and url.startswith('assets/') and '..' not in url.split('/')):raise HTTPException(422,'Usa una URL http/https o una ruta assets/ válida.')
        elif label=='correo' and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',value):raise HTTPException(422,'Correo no válido.')
        elif '<' in value or '>' in value:raise HTTPException(422,'Escribe contenido de texto sin etiquetas HTML.')
    return target,field,value

def set_setting(db,key,value):
    row=db.get(Setting,key)
    if row:row.value=value
    else:db.add(Setting(key=key,value=value))
def apply(db,target,field,value,actor_id):
    if target=='sga':
        patch={field:value}
        if field=='landing_carousel_urls':patch['landing_carousel_slides_json']=''
        before={key:({'exists':True,'value':db.get(Setting,key).value} if db.get(Setting,key) else {'exists':False,'value':None}) for key in patch}
        for key,text_value in patch.items():set_setting(db,key,text_value)
        return before,patch
    from app.api.v1.endpoints.corporate import sanitize
    row=db.get(CorporatePage,'analematica');original=json.loads(row.payload) if row else {};config=copy.deepcopy(original);part=config
    keys=field.split('.')
    for key in keys[:-1]:part=part.setdefault(key,{})
    part[keys[-1]]=value;config=sanitize(config)
    revision=row.revision if row else 0
    if row:
        changed=db.execute(update(CorporatePage).where(CorporatePage.key=='analematica',CorporatePage.revision==revision).values(payload=json.dumps(config),revision=revision+1)).rowcount
        if not changed:raise HTTPException(409,'La landing cambió durante la orden. Recarga antes de reintentar.')
    else:db.add(CorporatePage(key='analematica',payload=json.dumps(config),updated_by=actor_id,revision=1))
    return {'config':original,'revision':revision},{'config':config,'revision':revision+1}

def undo(db,actor,row_id):
    previous=db.get(CorporateCommand,row_id)
    if not previous or previous.actor_id!=actor.user.id or previous.status!='executed' or previous.operation=='undo':raise HTTPException(404,'No hay una orden de contenido reversible con ese identificador.')
    if previous.undone_by:raise HTTPException(409,'Esta orden ya fue deshecha.')
    before=json.loads(previous.before);after=json.loads(previous.after)
    if previous.target=='sga':
        for key,value in after.items():
            current=db.get(Setting,key)
            if not current or current.value!=value:raise HTTPException(409,'El contenido cambió después de esa orden; no se sobrescribió.')
        for key,snapshot in before.items():
            current=db.get(Setting,key)
            if snapshot['exists']:current.value=snapshot['value']
            else:db.delete(current)
    else:
        current=db.get(CorporatePage,'analematica')
        if not current or current.revision!=after['revision'] or json.loads(current.payload)!=after['config']:raise HTTPException(409,'La landing cambió después de esa orden; no se sobrescribió.')
        current.payload=json.dumps(before['config']);current.revision+=1;current.updated_by=actor.user.id
    return previous

def execute(db,actor,command,target,request_id):
    db.query(CorporateOwner).filter_by(id=1).with_for_update().one()
    fingerprint=hashlib.sha256(json.dumps([command,target],ensure_ascii=False).encode()).hexdigest();existing=db.get(CorporateCommand,request_id)
    if existing:
        if existing.actor_id!=actor.user.id or existing.request_hash!=fingerprint:raise HTTPException(409,'La referencia ya corresponde a otra orden.')
        return public_result(existing)
    clean=normalized(command).strip(' .!?¿¡');before={};after={};previous=None
    if clean in READS:
        operation=READS[clean];data=read(db,operation,actor);status='read';message='Consulta realizada en el servidor.'
    elif clean.startswith('deshacer '):
        row_id=command.split(maxsplit=1)[1].strip()
        try:uuid.UUID(row_id)
        except ValueError:raise HTTPException(422,'Indica el identificador de la orden que deseas deshacer.') from None
        previous=undo(db,actor,row_id);target=previous.target;operation='undo';status='executed';data={'orden_revertida':row_id};message='Cambio revertido y guardado en el servidor.'
    else:
        target,field,value=resolve_change(command,target);operation=field;before,after=apply(db,target,field,value,actor.user.id)
        if target=='analematica':
            db.flush();db.get(CorporatePage,'analematica').updated_by=actor.user.id
        status='executed';data={'campo':field,'valor':value,'destino':target};message='Contenido publicado en '+('SGA-CD' if target=='sga' else 'Analemática')+'.'
    result={'id':request_id,'status':status,'target':target,'operation':operation,'message':message,'data':data,'reversible':status=='executed' and operation!='undo'}
    audit=CorporateCommand(id=request_id,actor_id=actor.user.id,target=target,operation=operation,request_hash=fingerprint,status=status,before=json.dumps(before),after=json.dumps(after),result=json.dumps(result,ensure_ascii=False));db.add(audit)
    if previous:previous.undone_by=request_id
    try:db.commit()
    except IntegrityError:
        db.rollback();existing=db.get(CorporateCommand,request_id)
        if existing and existing.actor_id==actor.user.id and existing.request_hash==fingerprint:return public_result(existing)
        raise HTTPException(409,'La orden coincidió con otro cambio. No se confirmó su ejecución; recarga el estado.') from None
    return result
