from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import CustomUser


class IsOwnerOrReadOnly(BasePermission):
    """
    Permiso personalizado para permitir solo a los propietarios de un objeto editarlo.
    Asume que el modelo tiene un campo 'user' o 'usuario'.
    """
    def has_object_permission(self, request, view, obj):
        # Los permisos de lectura están permitidos para cualquier solicitud,
        # por lo que siempre permitiremos GET, HEAD u OPTIONS.
        if request.method in SAFE_METHODS:
            return True

        # El permiso de escritura solo se concede al propietario del objeto.
        # Intentamos buscar un campo 'user' o 'usuario'.
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user

        # Si el objeto es el propio usuario
        if isinstance(obj, CustomUser):
            return obj == request.user

        return False


class IsTurista(BasePermission):
    """
    Permiso personalizado para permitir el acceso solo a usuarios con el rol de TURISTA.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == CustomUser.Role.TURISTA
        )


class IsAdminOrFuncionario(BasePermission):
    """
    Permiso personalizado para permitir el acceso solo a usuarios con rol de
    ADMINISTRADOR o cualquier tipo de FUNCIONARIO.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in [
                CustomUser.Role.ADMIN,
                CustomUser.Role.ADMIN_NACIONAL,
                CustomUser.Role.ADMIN_DEPARTAMENTAL,
                CustomUser.Role.ADMIN_MUNICIPAL,
                CustomUser.Role.DIRECTIVO_NACIONAL,
                CustomUser.Role.DIRECTIVO_DEPARTAMENTAL,
                CustomUser.Role.DIRECTIVO_MUNICIPAL,
                CustomUser.Role.FUNCIONARIO_PROFESIONAL,
                CustomUser.Role.FUNCIONARIO_ASISTENCIAL,
            ]
        )


class IsAdmin(BasePermission):
    """
    Permiso personalizado para permitir el acceso solo a usuarios con el rol de ADMIN.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == CustomUser.Role.ADMIN
        )


class IsSuperAdmin(BasePermission):
    """
    Permiso exclusivo para el Super Administrador de la plataforma.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role == CustomUser.Role.ADMIN or request.user.is_superuser)
        )


class IsAdminOrFuncionarioForUserManagement(BasePermission):
    """
    Permiso personalizado para la gestión de usuarios.
    - ADMIN puede gestionar a todos los usuarios.
    - FUNCIONARIO (cualquier tipo) puede gestionar a PRESTADOR, ARTESANO y TURISTA.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # El Super Admin puede hacer todo
        if user.role == CustomUser.Role.ADMIN:
            return True

        # Los funcionarios pueden listar, pero el filtrado se hace en la vista.
        if view.action in ['list', 'retrieve']:
            return True

        # Para crear, los funcionarios solo pueden crear roles de menor jerarquía
        if view.action == 'create':
            target_role = request.data.get('role')

            # Jerarquía Gubernamental
            if user.role == CustomUser.Role.DIRECTIVO_NACIONAL:
                 allowed_target_roles = [
                     CustomUser.Role.DIRECTIVO_DEPARTAMENTAL,
                     CustomUser.Role.DIRECTIVO_MUNICIPAL,
                     CustomUser.Role.FUNCIONARIO_PROFESIONAL,
                     CustomUser.Role.FUNCIONARIO_TECNICO,
                     CustomUser.Role.FUNCIONARIO_ASISTENCIAL,
                 ]
            elif user.role == CustomUser.Role.DIRECTIVO_DEPARTAMENTAL:
                 allowed_target_roles = [
                     CustomUser.Role.DIRECTIVO_MUNICIPAL,
                     CustomUser.Role.FUNCIONARIO_PROFESIONAL,
                     CustomUser.Role.FUNCIONARIO_TECNICO,
                     CustomUser.Role.FUNCIONARIO_ASISTENCIAL,
                 ]
            elif user.role == CustomUser.Role.DIRECTIVO_MUNICIPAL:
                 allowed_target_roles = [
                     CustomUser.Role.FUNCIONARIO_PROFESIONAL,
                     CustomUser.Role.FUNCIONARIO_TECNICO,
                     CustomUser.Role.FUNCIONARIO_ASISTENCIAL,
                 ]
            else:
                 allowed_target_roles = []

            # Roles Base siempre permitidos para directivos/funcionarios
            allowed_target_roles += [
                CustomUser.Role.PRESTADOR,
                CustomUser.Role.ARTESANO,
                CustomUser.Role.TURISTA,
                CustomUser.Role.DELIVERY_DRIVER,
                CustomUser.Role.BUSINESS_OWNER
            ]
            return target_role in allowed_target_roles

        # Para otras acciones, se necesita un objeto, así que se delega a has_object_permission
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == CustomUser.Role.ADMIN:
            return True

        is_funcionario = user.role in [
            CustomUser.Role.ADMIN_NACIONAL,
            CustomUser.Role.ADMIN_DEPARTAMENTAL,
            CustomUser.Role.ADMIN_MUNICIPAL,
            CustomUser.Role.DIRECTIVO_NACIONAL,
            CustomUser.Role.DIRECTIVO_DEPARTAMENTAL,
            CustomUser.Role.DIRECTIVO_MUNICIPAL,
            CustomUser.Role.FUNCIONARIO_PROFESIONAL,
            CustomUser.Role.FUNCIONARIO_TECNICO,
            CustomUser.Role.FUNCIONARIO_ASISTENCIAL,
        ]

        if is_funcionario:
            target_role = obj.role
            allowed_target_roles = [
                CustomUser.Role.PRESTADOR,
                CustomUser.Role.ARTESANO,
                CustomUser.Role.TURISTA,
                CustomUser.Role.DELIVERY_DRIVER,
                CustomUser.Role.FUNCIONARIO_PROFESIONAL,
                CustomUser.Role.FUNCIONARIO_TECNICO,
                CustomUser.Role.FUNCIONARIO_ASISTENCIAL,
            ]
            return target_role in allowed_target_roles

        return False


class IsAnyAdminOrDirectivo(BasePermission):
    """
    Permiso personalizado para permitir el acceso a cualquier tipo de Administrador
    o a un Funcionario Directivo.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in [
                CustomUser.Role.ADMIN,
                CustomUser.Role.ADMIN_NACIONAL,
                CustomUser.Role.ADMIN_DEPARTAMENTAL,
                CustomUser.Role.ADMIN_MUNICIPAL,
                CustomUser.Role.DIRECTIVO_NACIONAL,
                CustomUser.Role.DIRECTIVO_DEPARTAMENTAL,
                CustomUser.Role.DIRECTIVO_MUNICIPAL,
            ]
        )


class IsPrestador(BasePermission):
    """
    Permiso personalizado para permitir el acceso solo a usuarios con el rol de PRESTADOR.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'perfil_prestador')
            and request.user.role == CustomUser.Role.PRESTADOR
        )

class IsPrestadorOwner(BasePermission):
    """
    Permite el acceso solo si el objeto que se está viendo/editando
    pertenece al prestador de servicios que está logueado.
    """
    def has_object_permission(self, request, view, obj):
        # Asumimos que el obj (ej. Producto, RegistroCliente) tiene un campo 'prestador'
        # que es una FK a PrestadorServicio.
        if hasattr(obj, 'prestador'):
            return obj.prestador == request.user.perfil_prestador
        return False


class CanManageAtractivos(BasePermission):
    """
    Permiso para gestionar Atractivos Turísticos.
    - Admins/Funcionarios: Tienen control total.
    - Guías de Turismo: Pueden crear atractivos y solo gestionar los propios.
    - Todos: Pueden ver la lista y los detalles.
    """
    def has_permission(self, request, view):
        user = request.user

        # Permitir siempre métodos seguros (GET, HEAD, OPTIONS)
        if view.action in ['list', 'retrieve']:
            return True

        # Si no es un método seguro, el usuario debe estar autenticado
        if not user or not user.is_authenticated:
            return False

        # El permiso para crear (POST)
        if view.action == 'create':
            if user.role in [CustomUser.Role.ADMIN, CustomUser.Role.FUNCIONARIO_DIRECTIVO, CustomUser.Role.FUNCIONARIO_PROFESIONAL]:
                return True
            # La lógica de permisos basada en CategoriaPrestador ha sido comentada
            # porque el modelo fue movido a otro dominio. Esto requerirá una
            # refactorización futura basada en servicios.
            # if user.role == CustomUser.Role.PRESTADOR:
            #     try:
            #         # Usamos el slug que es más confiable que el nombre
            #         guia_categoria = CategoriaPrestador.objects.get(slug='guias-de-turismo')
            #         return user.perfil_prestador.categoria == guia_categoria
            #     except (CategoriaPrestador.DoesNotExist, AttributeError):
            #         return False
            return False

        # Para otras acciones de escritura (update, partial_update, destroy),
        # el permiso se basa en el objeto, así que devolvemos True aquí
        # y dejamos que has_object_permission haga el trabajo.
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Permitir siempre métodos seguros (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True

        # Si no es un método seguro, el usuario debe estar autenticado
        if not user or not user.is_authenticated:
            return False

        # Admins y Funcionarios pueden editar/borrar cualquier atractivo.
        if user.role in [
            CustomUser.Role.ADMIN,
            CustomUser.Role.ADMIN_NACIONAL,
            CustomUser.Role.ADMIN_DEPARTAMENTAL,
            CustomUser.Role.ADMIN_MUNICIPAL,
            CustomUser.Role.DIRECTIVO_NACIONAL,
            CustomUser.Role.DIRECTIVO_DEPARTAMENTAL,
            CustomUser.Role.DIRECTIVO_MUNICIPAL,
            CustomUser.Role.FUNCIONARIO_PROFESIONAL,
        ]:
            return True

        # El autor del atractivo puede gestionarlo.
        # Esto cubre al guía que lo creó.
        return obj.autor == user


class IsEntityAdmin(BasePermission):
    """
    Permiso para permitir la gestión de una entidad solo a su administrador.
    """
    message = "No tienes permisos de administrador para esta entidad."

    def has_permission(self, request, view):
        # El usuario debe estar autenticado, tener el rol correcto, y tener un perfil con una entidad asignada.
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == CustomUser.Role.ADMIN_ENTIDAD and
            hasattr(request.user, 'profile') and
            request.user.profile.entity is not None
        )

    def has_object_permission(self, request, view, obj):
        # El objeto 'obj' es la instancia de la Entidad.
        # Verificamos si el perfil del usuario está asociado a esta entidad.
        try:
            return request.user.profile.entity == obj
        except AttributeError:
            # El usuario no tiene un perfil, por lo tanto no puede ser admin de ninguna entidad.
            return False


class IsCharacterizationManager(BasePermission):
    """
    Jerarquía de acceso para Caracterización y Verificación:
    - Super Administrador: Control total (CRUD).
    - Funcionarios (Directivo/Profesional): Monitoreo (Lectura) de todos. No editan.
    - Prestadores / Artesanos: Edición propia de sus formularios iniciales.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # El Admin puede todo
        if request.user.role == CustomUser.Role.ADMIN or request.user.is_superuser:
            return True

        # Funcionarios pueden leer todos
        if request.user.role in [
            CustomUser.Role.DIRECTIVO_NACIONAL,
            CustomUser.Role.DIRECTIVO_DEPARTAMENTAL,
            CustomUser.Role.DIRECTIVO_MUNICIPAL,
            CustomUser.Role.FUNCIONARIO_PROFESIONAL,
        ]:
            if request.method in SAFE_METHODS:
                return True
            return False # No pueden crear/borrar globalmente vía esta vista

        # Prestadores/Artesanos pueden crear y leer
        if request.user.role in [CustomUser.Role.BUSINESS_OWNER, CustomUser.Role.ARTESANO, CustomUser.Role.PRESTADOR]:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin puede todo
        if user.role == CustomUser.Role.ADMIN or user.is_superuser:
            return True

        # Funcionarios leen todo, no editan
        if user.role in [
            CustomUser.Role.DIRECTIVO_NACIONAL,
            CustomUser.Role.DIRECTIVO_DEPARTAMENTAL,
            CustomUser.Role.DIRECTIVO_MUNICIPAL,
            CustomUser.Role.FUNCIONARIO_PROFESIONAL,
        ]:
            return request.method in SAFE_METHODS

        # Prestadores solo editan/ven lo suyo
        # Intentamos obtener el propietario del objeto de caracterización
        owner = getattr(obj, 'usuario', None) or getattr(obj, 'user', None)
        return owner == user