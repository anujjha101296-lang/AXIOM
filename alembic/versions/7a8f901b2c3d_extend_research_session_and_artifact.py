"""Extend research_session and research_artifact models for Phase 7 Controlled Agent

Revision ID: 7a8f901b2c3d
Revises: 647aeab7ab1e
Create Date: 2026-08-12 23:56:50.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a8f901b2c3d'
down_revision: Union[str, Sequence[str], None] = '647aeab7ab1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to include Phase 7 research_sessions and research_artifacts fields."""
    op.add_column('research_sessions', sa.Column('goal', sa.Text(), nullable=False, server_default=''))
    op.add_column('research_sessions', sa.Column('max_steps', sa.Integer(), nullable=False, server_default='10'))
    op.add_column('research_sessions', sa.Column('max_tool_calls', sa.Integer(), nullable=False, server_default='15'))
    op.add_column('research_sessions', sa.Column('max_runtime_seconds', sa.Integer(), nullable=False, server_default='120'))
    op.add_column('research_sessions', sa.Column('step_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('research_sessions', sa.Column('tool_call_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('research_sessions', sa.Column('cancellation_requested', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('research_sessions', sa.Column('error_message', sa.Text(), nullable=True))
    op.add_column('research_sessions', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_research_sessions_status'), 'research_sessions', ['status'], unique=False)
    op.create_index(op.f('ix_research_artifacts_type'), 'research_artifacts', ['type'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_research_artifacts_type'), table_name='research_artifacts')
    op.drop_index(op.f('ix_research_sessions_status'), table_name='research_sessions')
    op.drop_column('research_sessions', 'completed_at')
    op.drop_column('research_sessions', 'error_message')
    op.drop_column('research_sessions', 'cancellation_requested')
    op.drop_column('research_sessions', 'tool_call_count')
    op.drop_column('research_sessions', 'step_count')
    op.drop_column('research_sessions', 'max_runtime_seconds')
    op.drop_column('research_sessions', 'max_tool_calls')
    op.drop_column('research_sessions', 'max_steps')
    op.drop_column('research_sessions', 'goal')
