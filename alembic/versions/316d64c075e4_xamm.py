"""xamm

Revision ID: 316d64c075e4
Revises: 39cf9236b4af
Create Date: 2023-08-03 03:26:23.508293

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '316d64c075e4'
down_revision = '39cf9236b4af'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('xamm_wallets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('wallet_addr', sa.String(), nullable=True),
    sa.Column('tf_sell', sa.Boolean(), nullable=True),
    sa.Column('tf_fill_or_kill', sa.Boolean(), nullable=True),
    sa.Column('tf_immediate_or_cancel', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_xamm_wallets_id'), 'xamm_wallets', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_xamm_wallets_id'), table_name='xamm_wallets')
    op.drop_table('xamm_wallets')
    # ### end Alembic commands ###