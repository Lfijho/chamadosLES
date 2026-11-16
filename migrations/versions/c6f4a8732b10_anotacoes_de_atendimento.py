"""Anotações de atendimento, preservando chamados e eventos existentes."""
from alembic import op
import sqlalchemy as sa

revision = "c6f4a8732b10"
down_revision = "ab92105d63e0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("ticket_notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ticket_id", sa.String(36), sa.ForeignKey("tickets.id"), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("length(trim(content)) BETWEEN 1 AND 5000", name="note_content_length"))
    op.create_index("ix_ticket_notes_ticket_id", "ticket_notes", ["ticket_id"])


def downgrade():
    if op.get_bind().execute(sa.text("SELECT count(*) FROM ticket_notes")).scalar():
        raise RuntimeError("Downgrade recusado: existem anotações que a Sprint 2 não representa.")
    op.drop_index("ix_ticket_notes_ticket_id", table_name="ticket_notes")
    op.drop_table("ticket_notes")
