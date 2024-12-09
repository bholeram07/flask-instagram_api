"""migrations

Revision ID: cca290d39507
Revises: 
Create Date: 2024-12-09 09:16:59.744249

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cca290d39507'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('first_name', sa.String(length=15), nullable=True),
    sa.Column('last_name', sa.String(length=20), nullable=True),
    sa.Column('bio', sa.String(length=120), nullable=True),
    sa.Column('profile_image', sa.LargeBinary(), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('_password', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('follows',
    sa.Column('follower_id', sa.UUID(), nullable=False),
    sa.Column('following_id', sa.UUID(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['following_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('follower_id', 'following_id')
    )
    op.create_table('post',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user', sa.UUID(), nullable=True),
    sa.Column('title', sa.String(length=40), nullable=False),
    sa.Column('content', sa.String(length=50), nullable=False),
    sa.Column('image', sa.String(length=255), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comment',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.Column('post_id', sa.UUID(), nullable=True),
    sa.Column('content', sa.String(length=50), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('like',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user', sa.UUID(), nullable=True),
    sa.Column('post', sa.UUID(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['post'], ['post.id'], ),
    sa.ForeignKeyConstraint(['user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('like')
    op.drop_table('comment')
    op.drop_table('post')
    op.drop_table('follows')
    op.drop_table('user')
    # ### end Alembic commands ###