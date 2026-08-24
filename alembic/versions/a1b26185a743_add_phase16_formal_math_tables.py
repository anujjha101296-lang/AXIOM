"""add_phase16_formal_math_tables

Revision ID: a1b26185a743
Revises: f5g67185a742
Create Date: 2026-08-24 20:42:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b26185a743'
down_revision: Union[str, Sequence[str], None] = 'f5g67185a742'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Formal Theorems Table
    op.create_table(
        'formal_theorems',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('claim_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('natural_language', sa.Text(), nullable=False),
        sa.Column('formal_statement', sa.Text(), nullable=False),
        sa.Column('language', sa.String(), nullable=False, server_default='LEAN4'),
        sa.Column('status', sa.String(), nullable=False, server_default='FORMALIZED'),
        sa.Column('assumptions_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('variables_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('quantifiers_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('metadata_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['claim_id'], ['graph_claims.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_formal_theorems_project_id'), 'formal_theorems', ['project_id'], unique=False)
    op.create_index(op.f('ix_formal_theorems_claim_id'), 'formal_theorems', ['claim_id'], unique=False)
    op.create_index(op.f('ix_formal_theorems_status'), 'formal_theorems', ['status'], unique=False)
    op.create_index(op.f('ix_formal_theorems_created_at'), 'formal_theorems', ['created_at'], unique=False)

    # 2. Formal Proofs Table
    op.create_table(
        'formal_proofs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('theorem_id', sa.String(), nullable=False),
        sa.Column('proof_script', sa.Text(), nullable=False),
        sa.Column('verifier_output', sa.Text(), nullable=False, server_default=''),
        sa.Column('compiler_version', sa.String(), nullable=False, server_default='Lean 4.7.0 / Z3 4.12.2'),
        sa.Column('status', sa.String(), nullable=False, server_default='PROOF_IN_PROGRESS'),
        sa.Column('is_sorry_free', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['theorem_id'], ['formal_theorems.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_formal_proofs_theorem_id'), 'formal_proofs', ['theorem_id'], unique=False)

    # 3. Counterexamples Table
    op.create_table(
        'counterexamples',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('theorem_id', sa.String(), nullable=False),
        sa.Column('domain', sa.String(), nullable=False, server_default='Finite domain'),
        sa.Column('assignment_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('witness_summary', sa.Text(), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['theorem_id'], ['formal_theorems.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_counterexamples_theorem_id'), 'counterexamples', ['theorem_id'], unique=False)

    # 4. Proof Artifacts Table
    op.create_table(
        'proof_artifacts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('theorem_id', sa.String(), nullable=False),
        sa.Column('proof_id', sa.String(), nullable=False),
        sa.Column('hash_id', sa.String(), nullable=False),
        sa.Column('artifact_uri', sa.Text(), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['theorem_id'], ['formal_theorems.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['proof_id'], ['formal_proofs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_proof_artifacts_theorem_id'), 'proof_artifacts', ['theorem_id'], unique=False)
    op.create_index(op.f('ix_proof_artifacts_proof_id'), 'proof_artifacts', ['proof_id'], unique=False)
    op.create_index(op.f('ix_proof_artifacts_hash_id'), 'proof_artifacts', ['hash_id'], unique=False)


def downgrade() -> None:
    op.drop_table('proof_artifacts')
    op.drop_table('counterexamples')
    op.drop_table('formal_proofs')
    op.drop_table('formal_theorems')
