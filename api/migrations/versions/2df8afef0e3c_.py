"""empty message

Revision ID: 2df8afef0e3c
Revises: 
Create Date: 2019-09-30 09:53:51.664836

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2df8afef0e3c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('convert_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('currency_code', sa.String(length=3), nullable=False),
    sa.Column('requested_amount', sa.DECIMAL(precision=8), nullable=False),
    sa.Column('oxr_price', sa.DECIMAL(), nullable=False),
    sa.Column('final_amount', sa.DECIMAL(precision=8), nullable=False),
    sa.Column('date_created', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('date_updated', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('request_id', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('convert_data')
    # ### end Alembic commands ###