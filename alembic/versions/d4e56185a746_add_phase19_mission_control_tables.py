"""add_phase19_mission_control_tables

Revision ID: d4e56185a746
Revises: c3d46185a745
Create Date: 2026-08-24 21:43:45.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e56185a746'
down_revision: Union[str, Sequence[str], None] = 'c3d46185a745'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Research Missions
    op.create_table(
        'research_missions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('objective', sa.Text(), nullable=False),
        sa.Column('state', sa.String(), nullable=False, server_default='INITIALIZED'),
        sa.Column('budget_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('current_iteration', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_research_missions_project_id'), 'research_missions', ['project_id'], unique=False)
    op.create_index(op.f('ix_research_missions_state'), 'research_missions', ['state'], unique=False)
    op.create_index(op.f('ix_research_missions_created_at'), 'research_missions', ['created_at'], unique=False)

    # 2. Mission Checkpoints
    op.create_table(
        'mission_checkpoints',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('mission_id', sa.String(), nullable=False),
        sa.Column('iteration', sa.Integer(), nullable=False),
        sa.Column('checkpoint_hash', sa.String(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('state_snapshot_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['mission_id'], ['research_missions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mission_checkpoints_mission_id'), 'mission_checkpoints', ['mission_id'], unique=False)
    op.create_index(op.f('ix_mission_checkpoints_checkpoint_hash'), 'mission_checkpoints', ['checkpoint_hash'], unique=False)
    op.create_index(op.f('ix_mission_checkpoints_created_at'), 'mission_checkpoints', ['created_at'], unique=False)

    # 3. Mission Tasks
    op.create_table(
        'mission_tasks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('mission_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('assigned_role', sa.String(), nullable=False, server_default='Mathematician'),
        sa.Column('state', sa.String(), nullable=False, server_default='PLANNED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['mission_id'], ['research_missions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mission_tasks_mission_id'), 'mission_tasks', ['mission_id'], unique=False)
    op.create_index(op.f('ix_mission_tasks_state'), 'mission_tasks', ['state'], unique=False)


def downgrade() -> None:
    op.drop_table('mission_tasks')
    op.drop_table('mission_checkpoints')
    op.drop_table('research_missions')
