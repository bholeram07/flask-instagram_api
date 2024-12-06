"""empty message

Revision ID: b1aa553b8138
Revises: 69d4361a3de4
Create Date: 2024-12-03 23:19:52.536965

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1aa553b8138'
down_revision = '69d4361a3de4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('post',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user', sa.UUID(), nullable=True),
    sa.Column('title', sa.String(length=40), nullable=False),
    sa.Column('content', sa.String(length=50), nullable=False),
    sa.Column('image_url', sa.String(length=255), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('post')
    # ### end Alembic commands ###