"""empty message

Revision ID: e84dd115890d
Revises: feee4805e309
Create Date: 2024-12-09 14:25:08.426652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e84dd115890d'
down_revision = 'feee4805e309'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.drop_constraint('comment_post_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('comment_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(None, 'post', ['post_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('like', schema=None) as batch_op:
        batch_op.drop_constraint('like_user_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_constraint('post_user_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('post_user_fkey', 'user', ['user'], ['id'])

    with op.batch_alter_table('like', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('like_user_fkey', 'user', ['user'], ['id'])

    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('comment_user_id_fkey', 'user', ['user_id'], ['id'])
        batch_op.create_foreign_key('comment_post_id_fkey', 'post', ['post_id'], ['id'])

    # ### end Alembic commands ###
