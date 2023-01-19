"""01_initial

Revision ID: 8efd28520fa4
Revises: 
Create Date: 2023-01-19 15:30:29.516666

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8efd28520fa4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('links',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('original_url', sqlalchemy_utils.types.url.URLType(), nullable=False),
    sa.Column('short_url', sqlalchemy_utils.types.url.URLType(), nullable=False),
    sa.Column('url_id', sa.String(length=8), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('usages_count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_links_url_id'), 'links', ['url_id'], unique=False)
    op.create_table('links_usages',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('link', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('client', sa.String(), nullable=False),
    sa.Column('use_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['link'], ['links.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_links_usages_use_at'), 'links_usages', ['use_at'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_links_usages_use_at'), table_name='links_usages')
    op.drop_table('links_usages')
    op.drop_index(op.f('ix_links_url_id'), table_name='links')
    op.drop_table('links')
    # ### end Alembic commands ###