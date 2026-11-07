"""Fail-closed institutional write scope, separate from public published content."""
from dataclasses import dataclass
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied,ValidationError
from rest_framework.permissions import BasePermission,SAFE_METHODS

@dataclass(frozen=True)
class Scope:
    entity: object
    level: str
    department_id: object
    municipality_id: object

ROLES={'ADMIN_ENTIDAD','ADMIN_NACIONAL','ADMIN_DEPARTAMENTAL','ADMIN_MUNICIPAL','DIRECTIVO_NACIONAL','DIRECTIVO_DEPARTAMENTAL','DIRECTIVO_MUNICIPAL','FUNCIONARIO_DIRECTIVO','FUNCIONARIO_PROFESIONAL','FUNCIONARIO_TECNICO','FUNCIONARIO_ASISTENCIAL'}

def privileged(user):return bool(user and user.is_authenticated and user.is_active and user.is_superuser)

def scope_for(user):
    if not user or not user.is_authenticated or not user.is_active or user.role not in ROLES:return None
    try:government=user.government_profile;profile=user.profile
    except (ObjectDoesNotExist,AttributeError):return None
    if not government.is_active or not profile.entity_id or profile.entity_id!=government.entity_id:return None
    level={'MUNICIPAL':'municipal','DEPARTAMENTAL':'departamental','NACIONAL':'nacional'}.get(government.nivel)
    if level!=government.entity.type:return None
    suffix={'municipal':'MUNICIPAL','departamental':'DEPARTAMENTAL','nacional':'NACIONAL'}[level]
    if user.role.startswith(('ADMIN_','DIRECTIVO_')) and user.role!='ADMIN_ENTIDAD' and not user.role.endswith(suffix):return None
    if level=='municipal':
        if not profile.municipality_id or not profile.department_id or profile.municipality.dept_id!=profile.department_id:return None
    if level=='departamental' and not profile.department_id:return None
    return Scope(profile.entity,level,profile.department_id,profile.municipality_id)

def scope_filter(scope):
    query=Q(entity_id=scope.entity.pk)
    if scope.level=='municipal':query &= Q(municipality_id=scope.municipality_id,department_id=scope.department_id)
    elif scope.level=='departamental':query &= Q(department_id=scope.department_id)
    return query

class InstitutionalAttractionPermission(BasePermission):
    def has_permission(self,request,view):
        if request.method in SAFE_METHODS:return True
        if privileged(request.user):return True
        action={'POST':'add','PUT':'change','PATCH':'change','DELETE':'delete'}.get(request.method)
        return bool(action and scope_for(request.user) and request.user.has_perm('api.'+action+'_atractivoturistico'))
    def has_object_permission(self,request,view,obj):
        if privileged(request.user):return True
        scope=scope_for(request.user)
        own=bool(scope and obj.entity_id==scope.entity.pk and (scope.level!='municipal' or (obj.municipality_id==scope.municipality_id and obj.department_id==scope.department_id)) and (scope.level!='departamental' or obj.department_id==scope.department_id))
        if request.method in SAFE_METHODS:return bool(obj.es_publicado or (own and request.user.has_perm('api.view_atractivoturistico')))
        if request.method=='DELETE' and obj.es_publicado and not request.user.has_perm('api.publish_atractivoturistico'):return False
        return own and self.has_permission(request,view)

def validate_write(user,data,instance=None):
    # Unspecified fields on PATCH retain their previous values.
    entity=data.get('entity',getattr(instance,'entity',None))
    department=data.get('department',getattr(instance,'department',None))
    municipality=data.get('municipality',getattr(instance,'municipality',None))
    scope=scope_for(user)
    if not privileged(user):
        if not scope:raise PermissionDenied('No hay una asignación institucional activa y coherente.')
        if entity is not None and entity.pk!=scope.entity.pk:raise PermissionDenied('No puedes cambiar la institución del registro.')
        entity=scope.entity
        if scope.level=='municipal':
            if municipality is not None and municipality.pk!=scope.municipality_id:raise PermissionDenied('Municipio fuera de tu jurisdicción.')
            if department is not None and department.pk!=scope.department_id:raise PermissionDenied('Departamento fuera de tu jurisdicción.')
            municipality=user.profile.municipality;department=user.profile.department
        elif scope.level=='departamental':
            if department is not None and department.pk!=scope.department_id:raise PermissionDenied('Departamento fuera de tu jurisdicción.')
            department=user.profile.department
        publication_change=('es_publicado' in data and data['es_publicado']!=getattr(instance,'es_publicado',False)) or bool(instance and instance.es_publicado and data)
        if publication_change and not user.has_perm('api.publish_atractivoturistico'):
            raise PermissionDenied('La publicación requiere un permiso funcional independiente.')
    if municipality and (not department or municipality.dept_id!=department.pk):raise ValidationError({'municipality':'El municipio no pertenece al departamento indicado.'})
    if entity is None:raise ValidationError({'entity':'El registro requiere una institución responsable.'})
    return {'entity':entity,'department':department,'municipality':municipality}
