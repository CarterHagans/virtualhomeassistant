"""Updating created on

Revision ID: 3c5c63683f4a
Revises: 7dcc889cc667
Create Date: 2023-06-02 01:46:31.708241

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c5c63683f4a'
down_revision = '7dcc889cc667'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('created_on',
               existing_type=sa.DATETIME(),
               type_=sa.String(length=500),
               existing_nullable=True,
               existing_server_default=sa.text('(CURRENT_TIMESTAMP)'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('created_on',
               existing_type=sa.String(length=500),
               type_=sa.DATETIME(),
               existing_nullable=True,
               existing_server_default=sa.text('(CURRENT_TIMESTAMP)'))

    # ### end Alembic commands ###
