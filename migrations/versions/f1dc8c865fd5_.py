"""empty message

Revision ID: f1dc8c865fd5
Revises: 53b21ea4c4b7
Create Date: 2024-12-29 14:34:34.351506

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1dc8c865fd5'
down_revision = '53b21ea4c4b7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('follow_request', schema=None) as batch_op:
        batch_op.add_column(sa.Column('following_id', sa.UUID(), nullable=True))
        batch_op.drop_constraint('follow_request_followed_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['following_id'], ['id'], ondelete='CASCADE')
        batch_op.drop_column('followed_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('follow_request', schema=None) as batch_op:
        batch_op.add_column(sa.Column('followed_id', sa.UUID(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('follow_request_followed_id_fkey', 'user', ['followed_id'], ['id'], ondelete='CASCADE')
        batch_op.drop_column('following_id')

    # ### end Alembic commands ###