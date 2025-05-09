"""create user, services and user_services

Revision ID: 389333d1da6c
Revises: 
Create Date: 2025-03-25 22:58:54.842389

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '389333d1da6c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('services',
    sa.Column('service_id', sa.Integer(), nullable=False),
    sa.Column('service_name', sa.String(length=64), nullable=False),
    sa.Column('service_url', sa.String(length=256), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('service_id')
    )
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_services_service_name'), ['service_name'], unique=True)

    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('_email', sa.String(length=128), nullable=False),
    sa.Column('_email_hash', sa.String(length=256), nullable=True),
    sa.Column('password_hash', sa.String(length=256), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('_email')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users__email_hash'), ['_email_hash'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

    op.create_table('user_services',
    sa.Column('user_services_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('service_id', sa.Integer(), nullable=False),
    sa.Column('_access_token', sa.String(length=256), nullable=False),
    sa.Column('_refresh_token', sa.String(length=256), nullable=True),
    sa.Column('expires_in', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['service_id'], ['services.service_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_services_id')
    )
    with op.batch_alter_table('user_services', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_services_service_id'), ['service_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_services_user_id'), ['user_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_services', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_services_user_id'))
        batch_op.drop_index(batch_op.f('ix_user_services_service_id'))

    op.drop_table('user_services')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_index(batch_op.f('ix_users__email_hash'))

    op.drop_table('users')
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_services_service_name'))

    op.drop_table('services')
    # ### end Alembic commands ###
