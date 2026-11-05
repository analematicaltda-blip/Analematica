"""add_performance_indexes_v1

Revision ID: c91a2e34f567
Revises: 36f3d0a15892
Create Date: 2025-05-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c91a2e34f567'
down_revision = '36f3d0a15892'
branch_labels = None
depends_on = None


def upgrade():
    # Performance indexes for tenant isolation & foreign key queries
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    indexes_to_create = [
        ('ix_usuarios_inquilino_id', 'usuarios', ['inquilino_id']),
        ('ix_alumnos_inquilino_id', 'alumnos', ['inquilino_id']),
        ('ix_alumnos_usuario_id', 'alumnos', ['usuario_id']),
        ('ix_mallas_inquilino_id', 'mallas_curriculares', ['inquilino_id']),
        ('ix_asignaturas_inquilino_id', 'asignaturas', ['inquilino_id']),
        ('ix_elementos_inquilino_estado', 'elementos', ['inquilino_id', 'estado']),
        ('ix_prestamos_inquilino_estado', 'prestamos', ['inquilino_id', 'estado']),
        ('ix_inscripciones_inquilino_alumno', 'inscripciones', ['inquilino_id', 'alumno_id']),
        ('ix_asistencias_inquilino_clase', 'asistencias', ['inquilino_id', 'clase_id']),
        ('ix_notificaciones_inquilino_usuario', 'notificaciones', ['inquilino_id', 'usuario_id', 'leida']),
    ]

    for idx_name, table_name, columns in indexes_to_create:
        if inspector.has_table(table_name):
            existing_cols = [c['name'] for c in inspector.get_columns(table_name)]
            if all(col in existing_cols for col in columns):
                op.create_index(idx_name, table_name, columns, unique=False, if_not_exists=True)


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    indexes_to_drop = [
        ('ix_notificaciones_inquilino_usuario', 'notificaciones'),
        ('ix_asistencias_inquilino_clase', 'asistencias'),
        ('ix_inscripciones_inquilino_alumno', 'inscripciones'),
        ('ix_prestamos_inquilino_estado', 'prestamos'),
        ('ix_elementos_inquilino_estado', 'elementos'),
        ('ix_asignaturas_inquilino_id', 'asignaturas'),
        ('ix_mallas_inquilino_id', 'mallas_curriculares'),
        ('ix_alumnos_usuario_id', 'alumnos'),
        ('ix_alumnos_inquilino_id', 'alumnos'),
        ('ix_usuarios_inquilino_id', 'usuarios'),
    ]

    for idx_name, table_name in indexes_to_drop:
        if inspector.has_table(table_name):
            op.drop_index(idx_name, table_name=table_name, if_exists=True)
