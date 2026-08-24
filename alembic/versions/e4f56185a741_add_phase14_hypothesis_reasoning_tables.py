"""add_phase14_hypothesis_reasoning_tables

Revision ID: e4f56185a741
Revises: d3e46185a740
Create Date: 2026-08-24 17:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4f56185a741'
down_revision: Union[str, Sequence[str], None] = 'd3e46185a740'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Hypotheses Table
    op.create_table(
        'hypotheses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('question_id', sa.String(), nullable=True),
        sa.Column('gap_id', sa.String(), nullable=True),
        sa.Column('claim', sa.Text(), nullable=False),
        sa.Column('motivation', sa.Text(), nullable=False, server_default=''),
        sa.Column('assumptions_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('verification_strategy', sa.Text(), nullable=False, server_default=''),
        sa.Column('status', sa.String(), nullable=False, server_default='PROPOSED'),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('rationale', sa.Text(), nullable=False, server_default=''),
        sa.Column('metadata_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['research_sessions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hypotheses_project_id'), 'hypotheses', ['project_id'], unique=False)
    op.create_index(op.f('ix_hypotheses_session_id'), 'hypotheses', ['session_id'], unique=False)
    op.create_index(op.f('ix_hypotheses_status'), 'hypotheses', ['status'], unique=False)
    op.create_index(op.f('ix_hypotheses_created_at'), 'hypotheses', ['created_at'], unique=False)

    # 2. Hypothesis Evidences Table
    op.create_table(
        'hypothesis_evidences',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('hypothesis_id', sa.String(), nullable=False),
        sa.Column('claim_id', sa.String(), nullable=True),
        sa.Column('chunk_id', sa.String(), nullable=True),
        sa.Column('source_id', sa.String(), nullable=True),
        sa.Column('supports', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('snippet', sa.Text(), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['hypothesis_id'], ['hypotheses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chunk_id'], ['document_chunks.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hypothesis_evidences_hypothesis_id'), 'hypothesis_evidences', ['hypothesis_id'], unique=False)

    # 3. Hypothesis Predictions Table
    op.create_table(
        'hypothesis_predictions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('hypothesis_id', sa.String(), nullable=False),
        sa.Column('prediction_text', sa.Text(), nullable=False),
        sa.Column('expected_observation', sa.Text(), nullable=False),
        sa.Column('conditions', sa.Text(), nullable=False, server_default=''),
        sa.Column('measurement', sa.Text(), nullable=False, server_default=''),
        sa.Column('falsifying_observation', sa.Text(), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['hypothesis_id'], ['hypotheses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hypothesis_predictions_hypothesis_id'), 'hypothesis_predictions', ['hypothesis_id'], unique=False)

    # 4. Hypothesis Critiques Table
    op.create_table(
        'hypothesis_critiques',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('hypothesis_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='VALID'),
        sa.Column('critique_text', sa.Text(), nullable=False),
        sa.Column('unsupported_assumptions_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('scope_errors_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('is_falsifiable', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['hypothesis_id'], ['hypotheses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hypothesis_critiques_hypothesis_id'), 'hypothesis_critiques', ['hypothesis_id'], unique=False)

    # 5. Hypothesis Revisions Table
    op.create_table(
        'hypothesis_revisions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('hypothesis_id', sa.String(), nullable=False),
        sa.Column('revision_index', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('previous_claim', sa.Text(), nullable=False),
        sa.Column('new_claim', sa.Text(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['hypothesis_id'], ['hypotheses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hypothesis_revisions_hypothesis_id'), 'hypothesis_revisions', ['hypothesis_id'], unique=False)

    # 6. Verification Plans Table
    op.create_table(
        'verification_plans',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('hypothesis_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('hypothesis_summary', sa.Text(), nullable=False),
        sa.Column('required_evidence_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('predictions_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('method', sa.String(), nullable=False, server_default='literature_research'),
        sa.Column('data_sources_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('success_criteria', sa.Text(), nullable=False, server_default=''),
        sa.Column('failure_criteria', sa.Text(), nullable=False, server_default=''),
        sa.Column('limitations_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['hypothesis_id'], ['hypotheses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_verification_plans_hypothesis_id'), 'verification_plans', ['hypothesis_id'], unique=False)
    op.create_index(op.f('ix_verification_plans_project_id'), 'verification_plans', ['project_id'], unique=False)


def downgrade() -> None:
    op.drop_table('verification_plans')
    op.drop_table('hypothesis_revisions')
    op.drop_table('hypothesis_critiques')
    op.drop_table('hypothesis_predictions')
    op.drop_table('hypothesis_evidences')
    op.drop_table('hypotheses')
