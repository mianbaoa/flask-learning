"""empty message

Revision ID: 6cddd8779deb
Revises: 
Create Date: 2016-12-03 09:49:12.041422

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6cddd8779deb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('follows',
    sa.Column('followed_id', sa.Integer(), nullable=False),
    sa.Column('follower_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('followed_id', 'follower_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('follows')
    ### end Alembic commands ###
