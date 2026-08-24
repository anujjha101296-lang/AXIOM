"""add_phase13_knowledge_graph_tables

Revision ID: d3e46185a740
Revises: c2e46185a739
Create Date: 2026-08-24 16:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3e46185a740'
down_revision: Union[str, Sequence[str], None] = 'c2e46185a739'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Graph Entities
    op.create_table(
        'graph_entities',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False, server_default='concept'),
        sa.Column('domain', sa.String(), nullable=False, server_default='general'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_graph_entities_project_id'), 'graph_entities', ['project_id'], unique=False)
    op.create_index(op.f('ix_graph_entities_name'), 'graph_entities', ['name'], unique=False)

    # 2. Graph Entity Aliases
    op.create_table(
        'graph_entity_aliases',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('entity_id', sa.String(), nullable=False),
        sa.Column('alias', sa.String(), nullable=False),
        sa.Column('source_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['entity_id'], ['graph_entities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_graph_entity_aliases_entity_id'), 'graph_entity_aliases', ['entity_id'], unique=False)
    op.create_index(op.f('ix_graph_entity_aliases_alias'), 'graph_entity_aliases', ['alias'], unique=False)

    # 3. Graph Claims
    op.create_table(
        'graph_claims',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('claim_text', sa.Text(), nullable=False),
        sa.Column('claim_type', sa.String(), nullable=False, server_default='FACTUAL'),
        sa.Column('epistemic_status', sa.String(), nullable=False, server_default='EXTRACTED'),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('metadata_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_graph_claims_project_id'), 'graph_claims', ['project_id'], unique=False)

    # 4. Graph Claim Evidences
    op.create_table(
        'graph_claim_evidences',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('claim_id', sa.String(), nullable=False),
        sa.Column('chunk_id', sa.String(), nullable=True),
        sa.Column('source_id', sa.String(), nullable=True),
        sa.Column('document_id', sa.String(), nullable=True),
        sa.Column('supports', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('snippet', sa.Text(), nullable=False, server_default=''),
        sa.Column('metadata_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['claim_id'], ['graph_claims.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chunk_id'], ['document_chunks.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_graph_claim_evidences_claim_id'), 'graph_claim_evidences', ['claim_id'], unique=False)

    # 5. Graph Relationships
    op.create_table(
        'graph_relationships',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('subject_entity_id', sa.String(), nullable=False),
        sa.Column('object_entity_id', sa.String(), nullable=False),
        sa.Column('predicate', sa.String(), nullable=False, server_default='RELATED_TO'),
        sa.Column('status', sa.String(), nullable=False, server_default='EXTRACTED'),
        sa.Column('metadata_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_entity_id'], ['graph_entities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['object_entity_id'], ['graph_entities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_graph_relationships_project_id'), 'graph_relationships', ['project_id'], unique=False)
    op.create_index(op.f('ix_graph_relationships_subject_entity_id'), 'graph_relationships', ['subject_entity_id'], unique=False)
    op.create_index(op.f('ix_graph_relationships_object_entity_id'), 'graph_relationships', ['object_entity_id'], unique=False)

    # 6. Graph Relationship Evidences
    op.create_table(
        'graph_relationship_evidences',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('relationship_id', sa.String(), nullable=False),
        sa.Column('chunk_id', sa.String(), nullable=True),
        sa.Column('source_id', sa.String(), nullable=True),
        sa.Column('snippet', sa.Text(), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['relationship_id'], ['graph_relationships.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chunk_id'], ['document_chunks.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_graph_relationship_evidences_relationship_id'), 'graph_relationship_evidences', ['relationship_id'], unique=False)

    # 7. Graph Contradictions
    op.create_table(
        'graph_contradictions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('claim_a_id', sa.String(), nullable=False),
        sa.Column('claim_b_id', sa.String(), nullable=False),
        sa.Column('contradiction_type', sa.String(), nullable=False, server_default='DIRECT'),
        sa.Column('reasoning', sa.Text(), nullable=False, server_default=''),
        sa.Column('resolved', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['claim_a_id'], ['graph_claims.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['claim_b_id'], ['graph_claims.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_graph_contradictions_project_id'), 'graph_contradictions', ['project_id'], unique=False)
    op.create_index(op.f('ix_graph_contradictions_claim_a_id'), 'graph_contradictions', ['claim_a_id'], unique=False)
    op.create_index(op.f('ix_graph_contradictions_claim_b_id'), 'graph_contradictions', ['claim_b_id'], unique=False)

    # 8. Graph Research Gaps
    op.create_table(
        'graph_research_gaps',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('gap_type', sa.String(), nullable=False, server_default='NO_EVIDENCE'),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False, server_default='MEDIUM'),
        sa.Column('target_entity_id', sa.String(), nullable=True),
        sa.Column('target_claim_id', sa.String(), nullable=True),
        sa.Column('target_question_id', sa.String(), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_graph_research_gaps_project_id'), 'graph_research_gaps', ['project_id'], unique=False)


def downgrade() -> None:
    op.drop_table('graph_research_gaps')
    op.drop_table('graph_contradictions')
    op.drop_table('graph_relationship_evidences')
    op.drop_table('graph_relationships')
    op.drop_table('graph_claim_evidences')
    op.drop_table('graph_claims')
    op.drop_table('graph_entity_aliases')
    op.drop_table('graph_entities')
