"""add_phase18_challenge_harness_tables

Revision ID: c3d46185a745
Revises: b2c36185a744
Create Date: 2026-08-24 21:33:30.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d46185a745'
down_revision: Union[str, Sequence[str], None] = 'b2c36185a744'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Benchmark Challenges
    op.create_table(
        'benchmark_challenges',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('version', sa.String(), nullable=False, server_default='AXIOM-MATH-001'),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('domain', sa.String(), nullable=False),
        sa.Column('difficulty_level', sa.String(), nullable=False, server_default='LEVEL_0_BASIC'),
        sa.Column('statement', sa.Text(), nullable=False),
        sa.Column('allowed_resources_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('time_budget_sec', sa.Integer(), nullable=False, server_default='300'),
        sa.Column('tool_budget_steps', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_benchmark_challenges_version'), 'benchmark_challenges', ['version'], unique=False)
    op.create_index(op.f('ix_benchmark_challenges_difficulty_level'), 'benchmark_challenges', ['difficulty_level'], unique=False)
    op.create_index(op.f('ix_benchmark_challenges_created_at'), 'benchmark_challenges', ['created_at'], unique=False)

    # 2. Benchmark Evaluation Runs
    op.create_table(
        'benchmark_evaluation_runs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('challenge_id', sa.String(), nullable=False),
        sa.Column('outcome', sa.String(), nullable=False, server_default='RESEARCH_PROGRESS'),
        sa.Column('score_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('failure_class', sa.String(), nullable=False, server_default='NONE'),
        sa.Column('runtime_sec', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('steps_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('proof_verified', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('counterexample_found', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['challenge_id'], ['benchmark_challenges.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_benchmark_evaluation_runs_challenge_id'), 'benchmark_evaluation_runs', ['challenge_id'], unique=False)
    op.create_index(op.f('ix_benchmark_evaluation_runs_outcome'), 'benchmark_evaluation_runs', ['outcome'], unique=False)
    op.create_index(op.f('ix_benchmark_evaluation_runs_failure_class'), 'benchmark_evaluation_runs', ['failure_class'], unique=False)
    op.create_index(op.f('ix_benchmark_evaluation_runs_created_at'), 'benchmark_evaluation_runs', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('benchmark_evaluation_runs')
    op.drop_table('benchmark_challenges')
