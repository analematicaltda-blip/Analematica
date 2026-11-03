"""add_master_catalog_and_specialties

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2025-05-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e2f3a4b5c6d7'
down_revision = 'd1e2f3a4b5c6'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. Add vocacion_institucional to inquilinos idempotently
    if inspector.has_table('inquilinos'):
        existing_cols = [c['name'] for c in inspector.get_columns('inquilinos')]
        if 'vocacion_institucional' not in existing_cols:
            op.add_column(
                'inquilinos',
                sa.Column('vocacion_institucional', sa.String(length=20), nullable=False, server_default='deportiva')
            )

    # 2. Create catalogo_especialidades idempotently
    if not inspector.has_table('catalogo_especialidades'):
        op.create_table(
            'catalogo_especialidades',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('vertical', sa.String(length=20), nullable=False),
            sa.Column('categoria', sa.String(length=100), nullable=False),
            sa.Column('codigo_canonico', sa.String(length=150), nullable=False),
            sa.Column('nombre', sa.String(length=200), nullable=False),
            sa.Column('es_estandar', sa.Boolean(), nullable=True, server_default='true'),
            sa.Column('creado_por_inquilino_id', sa.Integer(), nullable=True),
            sa.Column('activo', sa.Boolean(), nullable=True, server_default='true'),
            sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.ForeignKeyConstraint(['creado_por_inquilino_id'], ['inquilinos.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_catalogo_especialidades_id'), 'catalogo_especialidades', ['id'], unique=False)
        op.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_especialidad_clean ON catalogo_especialidades (vertical, lower(trim(nombre)))"
        )

    # 3. Create empresa_especialidades idempotently
    if not inspector.has_table('empresa_especialidades'):
        op.create_table(
            'empresa_especialidades',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('inquilino_id', sa.Integer(), nullable=False),
            sa.Column('especialidad_id', sa.Integer(), nullable=False),
            sa.Column('activa', sa.Boolean(), nullable=True, server_default='true'),
            sa.Column('fecha_adopcion', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.ForeignKeyConstraint(['inquilino_id'], ['inquilinos.id'], ),
            sa.ForeignKeyConstraint(['especialidad_id'], ['catalogo_especialidades.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('inquilino_id', 'especialidad_id', name='uq_empresa_especialidad')
        )
        op.create_index(op.f('ix_empresa_especialidades_id'), 'empresa_especialidades', ['id'], unique=False)

    # 4. Create profesor_especialidades idempotently
    if not inspector.has_table('profesor_especialidades'):
        op.create_table(
            'profesor_especialidades',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('usuario_id', sa.Integer(), nullable=False),
            sa.Column('empresa_especialidad_id', sa.Integer(), nullable=False),
            sa.Column('certificacion_avalada', sa.Boolean(), nullable=True, server_default='false'),
            sa.Column('nivel_academico', sa.String(length=100), nullable=True),
            sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
            sa.ForeignKeyConstraint(['empresa_especialidad_id'], ['empresa_especialidades.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_profesor_especialidades_id'), 'profesor_especialidades', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_profesor_especialidades_id'), table_name='profesor_especialidades')
    op.drop_table('profesor_especialidades')
    op.drop_index(op.f('ix_empresa_especialidades_id'), table_name='empresa_especialidades')
    op.drop_table('empresa_especialidades')
    op.execute("DROP INDEX IF EXISTS uq_especialidad_clean")
    op.drop_index(op.f('ix_catalogo_especialidades_id'), table_name='catalogo_especialidades')
    op.drop_table('catalogo_especialidades')
    op.drop_column('inquilinos', 'vocacion_institucional')
