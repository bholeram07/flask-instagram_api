"""empty message

Revision ID: c7e87da0f99f
Revises: 
Create Date: 2024-11-28 12:49:28.349689

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7e87da0f99f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blacklist_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('jti', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('blacklist_token', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_blacklist_token_jti'), ['jti'], unique=False)

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
    op.create_table('post',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user', sa.UUID(), nullable=True),
    sa.Column('title', sa.String(length=40), nullable=False),
    sa.Column('content', sa.String(length=50), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('post')
    op.drop_table('user')
    with op.batch_alter_table('blacklist_token', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_blacklist_token_jti'))

    op.drop_table('blacklist_token')
    # ### end Alembic commands ###