"""empty message

Revision ID: 991f3c238911
Revises: fc0c468fa1c5
Create Date: 2024-11-29 17:18:29.104872

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '991f3c238911'
down_revision = 'fc0c468fa1c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('post',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user', sa.UUID(), nullable=True),
    sa.Column('title', sa.String(length=40), nullable=False),
    sa.Column('content', sa.String(length=50), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('post')
    # ### end Alembic commands ###