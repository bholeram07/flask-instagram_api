"""empty message

Revision ID: 5c699ec6a5de
Revises: 991f3c238911
Create Date: 2024-11-29 17:25:04.288706

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c699ec6a5de'
down_revision = '991f3c238911'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('is_deleted',
               existing_type=sa.BOOLEAN(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('is_deleted',
               existing_type=sa.BOOLEAN(),
               nullable=False)

    # ### end Alembic commands ###