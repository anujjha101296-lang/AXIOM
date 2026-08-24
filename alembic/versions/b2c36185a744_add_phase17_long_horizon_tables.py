"""add_phase17_long_horizon_tables

Revision ID: b2c36185a744
Revises: a1b26185a743
Create Date: 2026-08-24 21:04:10.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c36185a744'
down_revision: Union[str, Sequence[str], None] = 'a1b26185a743'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Long Horizon Problems
    op.create_table(
        'long_horizon_problems',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('formal_statement', sa.Text(), nullable=False, server_default=''),
        sa.Column('status', sa.String(), nullable=False, server_default='PLANNED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_long_horizon_problems_project_id'), 'long_horizon_problems', ['project_id'], unique=False)
    op.create_index(op.f('ix_long_horizon_problems_status'), 'long_horizon_problems', ['status'], unique=False)
    op.create_index(op.f('ix_long_horizon_problems_created_at'), 'long_horizon_problems', ['created_at'], unique=False)

    # 2. Long Horizon Subproblems
    op.create_table(
        'long_horizon_subproblems',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('problem_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('statement', sa.Text(), nullable=False),
        sa.Column('dependencies_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('status', sa.String(), nullable=False, server_default='PLANNED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['problem_id'], ['long_horizon_problems.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_long_horizon_subproblems_problem_id'), 'long_horizon_subproblems', ['problem_id'], unique=False)
    op.create_index(op.f('ix_long_horizon_subproblems_status'), 'long_horizon_subproblems', ['status'], unique=False)

    # 3. Long Horizon Tasks
    op.create_table(
        'long_horizon_tasks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('subproblem_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('strategy', sa.String(), nullable=False, server_default='Decomposition'),
        sa.Column('state', sa.String(), nullable=False, server_default='PLANNED'),
        sa.Column('budget_steps', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('current_step', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['subproblem_id'], ['long_horizon_subproblems.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_long_horizon_tasks_subproblem_id'), 'long_horizon_tasks', ['subproblem_id'], unique=False)
    op.create_index(op.f('ix_long_horizon_tasks_state'), 'long_horizon_tasks', ['state'], unique=False)

    # 4. Long Horizon Attempts
    op.create_table(
        'long_horizon_attempts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('task_id', sa.String(), nullable=False),
        sa.Column('approach_description', sa.Text(), nullable=False),
        sa.Column('method', sa.String(), nullable=False, server_default='Direct Proof'),
        sa.Column('result_summary', sa.Text(), nullable=False, server_default=''),
        sa.Column('status', sa.String(), nullable=False, server_default='PROMISING'),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['long_horizon_tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_long_horizon_attempts_task_id'), 'long_horizon_attempts', ['task_id'], unique=False)

    # 5. Long Horizon Decisions
    op.create_table(
        'long_horizon_decisions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('problem_id', sa.String(), nullable=False),
        sa.Column('decision_type', sa.String(), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=False),
        sa.Column('critic_recommendation', sa.String(), nullable=False, server_default='CONTINUE'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['problem_id'], ['long_horizon_problems.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_long_horizon_decisions_problem_id'), 'long_horizon_decisions', ['problem_id'], unique=False)

    # 6. Long Horizon Milestones
    op.create_table(
        'long_horizon_milestones',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('problem_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('evidence_summary', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['problem_id'], ['long_horizon_problems.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_long_horizon_milestones_problem_id'), 'long_horizon_milestones', ['problem_id'], unique=False)

    # 7. Approach Memories
    op.create_table(
        'approach_memories',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('problem_id', sa.String(), nullable=False),
        sa.Column('approach_hash', sa.String(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='FAILED'),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['problem_id'], ['long_horizon_problems.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_approach_memories_problem_id'), 'approach_memories', ['problem_id'], unique=False)
    op.create_index(op.f('ix_approach_memories_approach_hash'), 'approach_memories', ['approach_hash'], unique=False)


def downgrade() -> None:
    op.drop_table('approach_memories')
    op.drop_table('long_horizon_milestones')
    op.drop_table('long_horizon_decisions')
    op.drop_table('long_horizon_attempts')
    op.drop_table('long_horizon_tasks')
    op.drop_table('long_horizon_subproblems')
    op.drop_table('long_horizon_problems')
