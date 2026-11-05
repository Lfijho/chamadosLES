"""Consulta e atendimento com preservação dos chamados anteriores."""
from alembic import op
import sqlalchemy as sa

revision = "ab92105d63e0"
down_revision = "7b2f18c4a901"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("tickets") as batch:
        batch.drop_constraint("ticket_initial_status", type_="check")
        batch.add_column(sa.Column("priority", sa.String(10), server_default="Média", nullable=False))
        batch.add_column(sa.Column("solution", sa.Text(), nullable=True))
        batch.add_column(sa.Column("completed_at", sa.DateTime(), nullable=True))
        batch.add_column(sa.Column("version", sa.Integer(), server_default="1", nullable=False))
        batch.create_check_constraint("ticket_status", "status IN ('Aberto','Em atendimento','Concluído')")
        batch.create_check_constraint("ticket_priority", "priority IN ('Baixa','Média','Alta')")
        batch.create_check_constraint("ticket_version", "version > 0")
        batch.create_check_constraint("ticket_completion",
            "(status = 'Concluído' AND solution IS NOT NULL AND length(trim(solution)) BETWEEN 1 AND 5000 "
            "AND completed_at IS NOT NULL) OR (status IN ('Aberto','Em atendimento') "
            "AND solution IS NULL AND completed_at IS NULL)")
    op.create_table("status_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ticket_id", sa.String(36), sa.ForeignKey("tickets.id"), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("old_status", sa.String(20), nullable=False),
        sa.Column("new_status", sa.String(20), nullable=False),
        sa.CheckConstraint("(old_status = 'Aberto' AND new_status = 'Em atendimento') OR "
                           "(old_status = 'Em atendimento' AND new_status = 'Concluído')", name="event_transition"))
    op.create_index("ix_status_events_ticket_id", "status_events", ["ticket_id"])


def downgrade():
    if op.get_bind().execute(sa.text("SELECT count(*) FROM tickets WHERE status != 'Aberto'")).scalar():
        raise RuntimeError("Downgrade recusado: existem atendimentos que a Sprint 1 não representa.")
    op.drop_index("ix_status_events_ticket_id", table_name="status_events")
    op.drop_table("status_events")
    with op.batch_alter_table("tickets") as batch:
        for name in ["ticket_status", "ticket_priority", "ticket_version", "ticket_completion"]:
            batch.drop_constraint(name, type_="check")
        for name in ["priority", "solution", "completed_at", "version"]:
            batch.drop_column(name)
        batch.create_check_constraint("ticket_initial_status", "status = 'Aberto'")
