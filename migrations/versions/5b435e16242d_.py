"""empty message

Revision ID: 5b435e16242d
Revises: 3e3ffcf756f4
Create Date: 2020-03-06 14:12:44.399482

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b435e16242d'
down_revision = '3e3ffcf756f4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_Show_start_time'), 'Show', ['start_time'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_Show_start_time'), table_name='Show')
    # ### end Alembic commands ###
