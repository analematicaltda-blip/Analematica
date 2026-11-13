"""add 52 week curriculum approval columns

Revision ID: g4f5e6d7c8b9
Revises: f3a4b5c6d7e8
Create Date: 2024-10-24 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'g4f5e6d7c8b9'
down_revision = 'f3a4b5c6d7e8'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('plan_curricular')]

    if 'estado_aprobacion' not in columns:
        op.add_column('plan_curricular', sa.Column('estado_aprobacion', sa.String(), nullable=False, server_default='borrador'))
    if 'observaciones_revision' not in columns:
        op.add_column('plan_curricular', sa.Column('observaciones_revision', sa.Text(), nullable=True))
    if 'vobo_coordinador_id' not in columns:
        op.add_column('plan_curricular', sa.Column('vobo_coordinador_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=True))
    if 'fecha_vobo' not in columns:
        op.add_column('plan_curricular', sa.Column('fecha_vobo', sa.DateTime(timezone=True), nullable=True))
    if 'ratificacion_jefe_id' not in columns:
        op.add_column('plan_curricular', sa.Column('ratificacion_jefe_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=True))
    if 'fecha_ratificacion' not in columns:
        op.add_column('plan_curricular', sa.Column('fecha_ratificacion', sa.DateTime(timezone=True), nullable=True))
    if 'version' not in columns:
        op.add_column('plan_curricular', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))

def downgrade():
    # Defensive drop columns if supported by dialect
    try:
        op.drop_column('plan_curricular', 'version')
        op.drop_column('plan_curricular', 'fecha_ratificacion')
        op.drop_column('plan_curricular', 'ratificacion_jefe_id')
        op.drop_column('plan_curricular', 'fecha_vobo')
        op.drop_column('plan_curricular', 'vobo_coordinador_id')
        op.drop_column('plan_curricular', 'observaciones_revision')
        op.drop_column('plan_curricular', 'estado_aprobacion')
    except Exception:
        pass
