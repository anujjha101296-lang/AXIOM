"""Add durable async research submission execution state.

Revision ID: 20260926_research_submission_status
Revises: 20260914_research_run_events
"""
from alembic import op
import sqlalchemy as sa

revision = "20260926_research_submission_status"
down_revision = "20260914_research_run_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "research_submissions",
        sa.Column("status", sa.String(length=32), nullable=False, server_default="QUEUED"),
    )
    op.add_column(
        "research_submissions",
        sa.Column("heartbeat_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        "UPDATE research_submissions SET heartbeat_at = created_at WHERE heartbeat_at IS NULL"
    )
    op.alter_column("research_submissions", "heartbeat_at", nullable=False)


def downgrade() -> None:
    op.drop_column("research_submissions", "heartbeat_at")
    op.drop_column("research_submissions", "status")
