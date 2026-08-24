"""add_phase20_control_plane_tables

Revision ID: e5f66185a747
Revises: d4e56185a746
Create Date: 2026-08-24 22:29:18.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f66185a747'
down_revision: Union[str, Sequence[str], None] = 'd4e56185a746'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Agent Profiles
    op.create_table(
        'agent_profiles',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('allowed_tools_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('allowed_models_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('max_steps', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('max_tokens', sa.Integer(), nullable=False, server_default='100000'),
        sa.Column('timeout_sec', sa.Integer(), nullable=False, server_default='300'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role')
    )
    op.create_index(op.f('ix_agent_profiles_name'), 'agent_profiles', ['name'], unique=False)
    op.create_index(op.f('ix_agent_profiles_role'), 'agent_profiles', ['role'], unique=True)

    # 2. Domain Events
    op.create_table(
        'domain_events',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('mission_id', sa.String(), nullable=True),
        sa.Column('task_id', sa.String(), nullable=True),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('actor', sa.String(), nullable=False, server_default='system'),
        sa.Column('payload_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_domain_events_project_id'), 'domain_events', ['project_id'], unique=False)
    op.create_index(op.f('ix_domain_events_mission_id'), 'domain_events', ['mission_id'], unique=False)
    op.create_index(op.f('ix_domain_events_task_id'), 'domain_events', ['task_id'], unique=False)
    op.create_index(op.f('ix_domain_events_event_type'), 'domain_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_domain_events_timestamp'), 'domain_events', ['timestamp'], unique=False)

    # 3. Worker Nodes
    op.create_table(
        'worker_nodes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('hostname', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='AVAILABLE'),
        sa.Column('current_task_id', sa.String(), nullable=True),
        sa.Column('last_heartbeat', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_worker_nodes_hostname'), 'worker_nodes', ['hostname'], unique=False)
    op.create_index(op.f('ix_worker_nodes_status'), 'worker_nodes', ['status'], unique=False)
    op.create_index(op.f('ix_worker_nodes_last_heartbeat'), 'worker_nodes', ['last_heartbeat'], unique=False)


def downgrade() -> None:
    op.drop_table('worker_nodes')
    op.drop_table('domain_events')
    op.drop_table('agent_profiles')
