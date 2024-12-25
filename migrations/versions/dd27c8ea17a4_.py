"""empty message

Revision ID: dd27c8ea17a4
Revises: 
Create Date: 2024-12-25 10:32:55.039234

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd27c8ea17a4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_or_video', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('is_enable_comment', sa.Boolean(), nullable=True))
        batch_op.drop_column('image')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
        batch_op.drop_column('is_enable_comment')
        batch_op.drop_column('image_or_video')

    # ### end Alembic commands ###
