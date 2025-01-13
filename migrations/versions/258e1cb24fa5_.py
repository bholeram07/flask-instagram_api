"""empty message

Revision ID: 258e1cb24fa5
Revises: 179ec8d5f15f
Create Date: 2025-01-13 16:57:56.722356

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '258e1cb24fa5'
down_revision = '179ec8d5f15f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('follow_request', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['id'])

    with op.batch_alter_table('story_view', schema=None) as batch_op:
        batch_op.drop_column('deleted_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('is_deleted')
        batch_op.drop_column('updated_at')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index('idx_id')
        batch_op.drop_index('idx_is_verified_active')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index('idx_is_verified_active', ['is_verified', 'is_active'], unique=False)
        batch_op.create_index('idx_id', ['id'], unique=False)

    with op.batch_alter_table('story_view', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('is_deleted', sa.BOOLEAN(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))

    with op.batch_alter_table('follow_request', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    # ### end Alembic commands ###