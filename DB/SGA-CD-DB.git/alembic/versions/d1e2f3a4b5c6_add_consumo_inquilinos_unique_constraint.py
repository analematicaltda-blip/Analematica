"""add_consumo_inquilinos_unique_constraint

Revision ID: d1e2f3a4b5c6
Revises: c91a2e34f567
Create Date: 2025-05-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd1e2f3a4b5c6'
down_revision = 'c91a2e34f567'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create table consumo_inquilinos if not exists
    op.create_table(
        'consumo_inquilinos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('inquilino_id', sa.Integer(), nullable=False),
        sa.Column('periodo', sa.String(), nullable=False),
        sa.Column('capacidad', sa.String(), nullable=False),
        sa.Column('cantidad_usada', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ultima_actualizacion', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['inquilino_id'], ['inquilinos.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('inquilino_id', 'periodo', 'capacidad', name='uq_consumo_inquilino_periodo_capacidad')
    )
    op.create_index(op.f('ix_consumo_inquilinos_id'), 'consumo_inquilinos', ['id'], unique=False)
    op.create_index(op.f('ix_consumo_inquilinos_inquilino_id'), 'consumo_inquilinos', ['inquilino_id'], unique=False)
    op.create_index(op.f('ix_consumo_inquilinos_periodo'), 'consumo_inquilinos', ['periodo'], unique=False)
    op.create_index(op.f('ix_consumo_inquilinos_capacidad'), 'consumo_inquilinos', ['capacidad'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_consumo_inquilinos_capacidad'), table_name='consumo_inquilinos')
    op.drop_index(op.f('ix_consumo_inquilinos_periodo'), table_name='consumo_inquilinos')
    op.drop_index(op.f('ix_consumo_inquilinos_inquilino_id'), table_name='consumo_inquilinos')
    op.drop_index(op.f('ix_consumo_inquilinos_id'), table_name='consumo_inquilinos')
    op.drop_table('consumo_inquilinos')
