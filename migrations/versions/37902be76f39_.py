"""empty message

Revision ID: 37902be76f39
Revises: 258e1cb24fa5
Create Date: 2025-01-13 17:02:25.092333

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37902be76f39'
down_revision = '258e1cb24fa5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('story_view', schema=None) as batch_op:
        batch_op.add_column(sa.Column('viewed_at', sa.DateTime(timezone=True), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('story_view', schema=None) as batch_op:
        batch_op.drop_column('viewed_at')

    # ### end Alembic commands ###