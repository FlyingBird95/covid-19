"""empty message

Revision ID: 2286baefdbc2
Revises: ca9ba145768e
Create Date: 2020-03-26 21:47:03.150005

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2286baefdbc2'
down_revision = 'ca9ba145768e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('locations', sa.Column('country_code', sa.String(length=10), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'locations', type_='unique')
    op.drop_column('locations', 'country_code')
    # ### end Alembic commands ###
