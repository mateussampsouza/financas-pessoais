"""replace repeat_monthly with recurrence fields

Revision ID: 63120ac3aec6
Revises: 278a3ae37a0c
Create Date: 2026-08-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63120ac3aec6'
down_revision: Union[str, Sequence[str], None] = '278a3ae37a0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('recurrence', sa.String(length=10), nullable=False, server_default='nunca'))
        batch_op.add_column(sa.Column('recurrence_quantity', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('recurrence_installment', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('recurrence_group_id', sa.String(length=36), nullable=True))
        batch_op.drop_column('repeat_monthly')

    op.create_index(op.f('ix_transactions_recurrence_group_id'), 'transactions', ['recurrence_group_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_transactions_recurrence_group_id'), table_name='transactions')

    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('repeat_monthly', sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.drop_column('recurrence_group_id')
        batch_op.drop_column('recurrence_installment')
        batch_op.drop_column('recurrence_quantity')
        batch_op.drop_column('recurrence')
