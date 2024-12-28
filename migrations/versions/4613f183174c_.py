"""empty message

Revision ID: 4613f183174c
Revises: 65b0ab58c815
Create Date: 2024-12-26 16:20:17.318255

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4613f183174c'
down_revision = '65b0ab58c815'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('like', schema=None) as batch_op:
        batch_op.add_column(sa.Column('story', sa.UUID(), nullable=True))
        batch_op.add_column(sa.Column('comment', sa.UUID(), nullable=True))
        batch_op.alter_column('user',
               existing_type=sa.UUID(),
               nullable=False)
        batch_op.create_foreign_key(None, 'comment', ['comment'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(None, 'story', ['story'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('like', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('user',
               existing_type=sa.UUID(),
               nullable=True)
        batch_op.drop_column('comment')
        batch_op.drop_column('story')

    # ### end Alembic commands ###