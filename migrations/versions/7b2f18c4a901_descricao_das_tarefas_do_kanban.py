"""Acrescenta descrição às tarefas do quadro acadêmico, preservando registros."""
from alembic import op
import sqlalchemy as sa

revision = "7b2f18c4a901"
down_revision = "3c65b6acc942"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tasks", sa.Column("description", sa.Text(), nullable=False, server_default=""))


def downgrade():
    op.drop_column("tasks", "description")
