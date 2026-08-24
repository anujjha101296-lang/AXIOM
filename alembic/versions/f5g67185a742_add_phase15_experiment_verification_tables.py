"""add_phase15_experiment_verification_tables

Revision ID: f5g67185a742
Revises: e4f56185a741
Create Date: 2026-08-24 20:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5g67185a742'
down_revision: Union[str, Sequence[str], None] = 'e4f56185a741'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Experiments Table
    op.create_table(
        'experiments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('hypothesis_id', sa.String(), nullable=True),
        sa.Column('prediction_id', sa.String(), nullable=True),
        sa.Column('plan_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('objective', sa.Text(), nullable=False),
        sa.Column('code_body', sa.Text(), nullable=False),
        sa.Column('method', sa.String(), nullable=False, server_default='numerical_simulation'),
        sa.Column('parameters_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('resource_limits_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('status', sa.String(), nullable=False, server_default='PLANNED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['hypothesis_id'], ['hypotheses.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['plan_id'], ['verification_plans.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_experiments_project_id'), 'experiments', ['project_id'], unique=False)
    op.create_index(op.f('ix_experiments_hypothesis_id'), 'experiments', ['hypothesis_id'], unique=False)
    op.create_index(op.f('ix_experiments_status'), 'experiments', ['status'], unique=False)
    op.create_index(op.f('ix_experiments_created_at'), 'experiments', ['created_at'], unique=False)

    # 2. Experiment Runs Table
    op.create_table(
        'experiment_runs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('experiment_id', sa.String(), nullable=False),
        sa.Column('run_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(), nullable=False, server_default='PLANNED'),
        sa.Column('runtime_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('memory_bytes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('stdout', sa.Text(), nullable=False, server_default=''),
        sa.Column('stderr', sa.Text(), nullable=False, server_default=''),
        sa.Column('result_data_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('input_hash', sa.String(), nullable=False, server_default=''),
        sa.Column('spec_hash', sa.String(), nullable=False, server_default=''),
        sa.Column('seed', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['experiment_id'], ['experiments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_experiment_runs_experiment_id'), 'experiment_runs', ['experiment_id'], unique=False)

    # 3. Experiment Observations Table
    op.create_table(
        'experiment_observations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('experiment_id', sa.String(), nullable=False),
        sa.Column('run_id', sa.String(), nullable=False),
        sa.Column('observation_level', sa.String(), nullable=False, server_default='COMPUTATIONAL_OBSERVATION'),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('metrics_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('reproducibility_status', sa.String(), nullable=False, server_default='REPRODUCIBLE'),
        sa.Column('interpretation_status', sa.String(), nullable=False, server_default='SUPPORTED'),
        sa.Column('is_mathematical_proof', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('limitations_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['experiment_id'], ['experiments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['run_id'], ['experiment_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_experiment_observations_experiment_id'), 'experiment_observations', ['experiment_id'], unique=False)
    op.create_index(op.f('ix_experiment_observations_run_id'), 'experiment_observations', ['run_id'], unique=False)

    # 4. Experiment Verifications Table
    op.create_table(
        'experiment_verifications',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('experiment_id', sa.String(), nullable=False),
        sa.Column('run_id', sa.String(), nullable=False),
        sa.Column('verification_status', sa.String(), nullable=False, server_default='VERIFIED'),
        sa.Column('independent_method', sa.Text(), nullable=False),
        sa.Column('independent_result', sa.Text(), nullable=False),
        sa.Column('discrepancy', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['experiment_id'], ['experiments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['run_id'], ['experiment_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_experiment_verifications_experiment_id'), 'experiment_verifications', ['experiment_id'], unique=False)
    op.create_index(op.f('ix_experiment_verifications_run_id'), 'experiment_verifications', ['run_id'], unique=False)


def downgrade() -> None:
    op.drop_table('experiment_verifications')
    op.drop_table('experiment_observations')
    op.drop_table('experiment_runs')
    op.drop_table('experiments')
