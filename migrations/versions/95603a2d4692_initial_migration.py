"""initial migration

Revision ID: 95603a2d4692
Revises: 
Create Date: 2022-01-13 10:24:41.362558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '95603a2d4692'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('item_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=60), nullable=True),
    sa.Column('username', sa.String(length=60), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('first_name', sa.String(length=60), nullable=True),
    sa.Column('last_name', sa.String(length=60), nullable=True),
    sa.Column('is_mod', sa.Boolean(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_first_name'), 'users', ['first_name'], unique=False)
    op.create_index(op.f('ix_users_last_name'), 'users', ['last_name'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('vinyl_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('Catno', sa.String(length=50), nullable=True),
    sa.Column('Artist', sa.String(length=50), nullable=True),
    sa.Column('Album', sa.String(length=100), nullable=True),
    sa.Column('Sleeve_Grade', sa.String(length=10), nullable=True),
    sa.Column('Record_Grade', sa.String(length=10), nullable=True),
    sa.Column('Release_Year', sa.Integer(), nullable=True),
    sa.Column('Price', sa.Float(), nullable=True),
    sa.Column('Labels', sa.String(length=100), nullable=True),
    sa.Column('Genres', sa.String(length=100), nullable=True),
    sa.Column('Styles', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('item_type_id', sa.Integer(), nullable=True),
    sa.Column('entry_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['item_type_id'], ['item_type.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('item_images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('image_url', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('item_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('item_type_id', sa.Integer(), nullable=True),
    sa.Column('entry_date', sa.DateTime(), nullable=True),
    sa.Column('Comments', sa.String(length=200), nullable=True),
    sa.Column('Location', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
    sa.ForeignKeyConstraint(['item_type_id'], ['item_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('item_info')
    op.drop_table('item_images')
    op.drop_table('item')
    op.drop_table('vinyl_info')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_last_name'), table_name='users')
    op.drop_index(op.f('ix_users_first_name'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('item_type')
    # ### end Alembic commands ###