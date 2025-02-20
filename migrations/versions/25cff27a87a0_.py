"""empty message

Revision ID: 25cff27a87a0
Revises: d6a135bcf738
Create Date: 2025-01-14 11:27:03.625558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25cff27a87a0'
down_revision = 'd6a135bcf738'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('story', schema=None) as batch_op:
        batch_op.add_column(sa.Column('owner', sa.UUID(), nullable=True))
        batch_op.drop_constraint('story_story_owner_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['owner'], ['id'], ondelete='CASCADE')
        batch_op.drop_column('story_owner')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('story', schema=None) as batch_op:
        batch_op.add_column(sa.Column('story_owner', sa.UUID(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('story_story_owner_fkey', 'user', ['story_owner'], ['id'], ondelete='CASCADE')
        batch_op.drop_column('owner')

    # ### end Alembic commands ###
