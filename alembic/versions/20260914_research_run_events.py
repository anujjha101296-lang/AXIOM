"""Create durable scientific research run/event storage.

Revision ID: 20260914_research_run_events
Revises: e5f66185a747
"""
from alembic import op
import sqlalchemy as sa

revision = "20260914_research_run_events"
down_revision = "e5f66185a747"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "research_runs",
        sa.Column("run_id", sa.String(length=128), primary_key=True),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "research_events",
        sa.Column("run_id", sa.String(length=128), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.String(length=160), nullable=False, unique=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("stage", sa.String(length=64), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("run_id", "sequence"),
        sa.ForeignKeyConstraint(["run_id"], ["research_runs.run_id"], ondelete="CASCADE"),
    )
    op.create_index("ix_research_events_run_sequence", "research_events", ["run_id", "sequence"])
    op.create_table(
        "research_submissions",
        sa.Column("idempotency_key", sa.String(length=255), primary_key=True),
        sa.Column("request_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("run_id", sa.String(length=128), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["research_runs.run_id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_index("ix_research_events_run_sequence", table_name="research_events")
    op.drop_table("research_events")
    op.drop_table("research_submissions")
    op.drop_table("research_runs")
