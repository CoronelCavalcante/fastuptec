"""primeiro autogenerate usando o Base

Revision ID: 76df79401028
Revises: d32b24829ddb
Create Date: 2022-01-18 10:16:28.075597

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76df79401028'
down_revision = 'd32b24829ddb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('employee',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('manager', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('ordemdistribuida',
    sa.Column('id_employee', sa.Integer(), nullable=False),
    sa.Column('id_ordem_servico', sa.Integer(), nullable=False),
    sa.Column('id_poster', sa.Integer(), nullable=False),
    sa.Column('completed', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['id_employee'], ['employee.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['id_poster'], ['employee.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id_employee', 'id_ordem_servico')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ordemdistribuida')
    op.drop_table('employee')
    # ### end Alembic commands ###