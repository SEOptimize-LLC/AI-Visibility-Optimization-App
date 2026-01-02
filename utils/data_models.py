"""Pydantic data models for the AI Search Visibility Framework."""

from pydantic import BaseModel, Field
from typing import Any
from enum import Enum
from datetime import datetime


class EntityType(str, Enum):
    """Classification of entity types."""
    CORE = "core"  # Primary business entities
    SUPPORTING = "supporting"  # Secondary/contextual entities
    COMPETITOR = "competitor"  # Competitor entities
    ATTRIBUTE = "attribute"  # Entity attributes/properties


class RelationshipType(str, Enum):
    """Types of semantic relationships between entities."""
    IS_A = "is_a"
    PART_OF = "part_of"
    USED_FOR = "used_for"
    RELATES_TO = "relates_to"
    REQUIRES = "requires"
    ALTERNATIVE_TO = "alternative_to"
    ENABLES = "enables"
    CONTRASTS_WITH = "contrasts_with"


class IntentType(str, Enum):
    """Search intent classification."""
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    COMMERCIAL = "commercial"
    TRANSACTIONAL = "transactional"
    LOCAL = "local"


class ContentPriority(str, Enum):
    """Content creation priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# =============================================================================
# Step 1: Ontology Models
# =============================================================================

class Entity(BaseModel):
    """Represents a semantic entity in the brand ontology."""
    id: str = Field(..., description="Unique identifier for the entity")
    name: str = Field(..., description="Primary name of the entity")
    type: EntityType = Field(default=EntityType.CORE)
    description: str | None = Field(default=None)
    aliases: list[str] = Field(default_factory=list, description="Alternative names/synonyms")
    attributes: dict[str, Any] = Field(default_factory=dict)
    commercial_value: float = Field(default=0.5, ge=0.0, le=1.0, description="Business value score")
    semantic_centrality: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance in ontology")
    source_urls: list[str] = Field(default_factory=list, description="URLs where entity appears")

    def __hash__(self):
        return hash(self.id)


class Relationship(BaseModel):
    """Represents a semantic relationship between two entities."""
    source_id: str = Field(..., description="Source entity ID")
    target_id: str = Field(..., description="Target entity ID")
    relationship_type: RelationshipType
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    context: str | None = Field(default=None, description="Context or evidence for relationship")
    bidirectional: bool = Field(default=False)


class Ontology(BaseModel):
    """Complete brand ontology with entities and relationships."""
    brand_name: str
    entities: list[Entity] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    version: str = Field(default="1.0")

    def get_entity(self, entity_id: str) -> Entity | None:
        """Get entity by ID."""
        return next((e for e in self.entities if e.id == entity_id), None)

    def get_related_entities(self, entity_id: str) -> list[tuple[Entity, Relationship]]:
        """Get all entities related to the given entity."""
        related = []
        for rel in self.relationships:
            if rel.source_id == entity_id:
                entity = self.get_entity(rel.target_id)
                if entity:
                    related.append((entity, rel))
            elif rel.bidirectional and rel.target_id == entity_id:
                entity = self.get_entity(rel.source_id)
                if entity:
                    related.append((entity, rel))
        return related

    def entity_count_by_type(self) -> dict[str, int]:
        """Count entities by type."""
        counts: dict[str, int] = {}
        for entity in self.entities:
            counts[entity.type.value] = counts.get(entity.type.value, 0) + 1
        return counts


# =============================================================================
# Step 3: Taxonomy Models
# =============================================================================

class TaxonomyNode(BaseModel):
    """A node in the taxonomy hierarchy."""
    id: str
    name: str
    parent_id: str | None = None
    entity_ids: list[str] = Field(default_factory=list, description="Associated entity IDs")
    level: int = Field(default=0, description="Depth in hierarchy (0 = root)")
    facets: list[str] = Field(default_factory=list, description="Cross-cutting tags")
    seo_title: str | None = None
    seo_description: str | None = None
    target_url: str | None = Field(default=None, description="Target URL for this category")
    internal_links_to: list[str] = Field(default_factory=list, description="IDs of nodes to link to")


class Taxonomy(BaseModel):
    """Complete taxonomy structure with hierarchies and facets."""
    brand_name: str
    nodes: list[TaxonomyNode] = Field(default_factory=list)
    facet_definitions: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Facet name -> possible values"
    )
    created_at: datetime = Field(default_factory=datetime.now)

    def get_root_nodes(self) -> list[TaxonomyNode]:
        """Get all root-level taxonomy nodes."""
        return [n for n in self.nodes if n.parent_id is None]

    def get_children(self, node_id: str) -> list[TaxonomyNode]:
        """Get direct children of a node."""
        return [n for n in self.nodes if n.parent_id == node_id]

    def get_node_path(self, node_id: str) -> list[TaxonomyNode]:
        """Get path from root to node."""
        path = []
        current = next((n for n in self.nodes if n.id == node_id), None)
        while current:
            path.insert(0, current)
            current = next((n for n in self.nodes if n.id == current.parent_id), None)
        return path


# =============================================================================
# Step 4: Query Mapping Models
# =============================================================================

class Query(BaseModel):
    """A search query with intent and metadata."""
    query_text: str
    intent: IntentType
    entity_ids: list[str] = Field(default_factory=list)
    estimated_volume: int | None = None
    difficulty: float | None = Field(default=None, ge=0.0, le=1.0)
    priority: ContentPriority = ContentPriority.MEDIUM
    serp_features: list[str] = Field(default_factory=list)
    fanout_pattern: str | None = Field(default=None, description="Which pattern generated this")


class QueryCluster(BaseModel):
    """A cluster of related queries around an entity."""
    id: str
    primary_entity_id: str
    primary_entity_name: str
    queries: list[Query] = Field(default_factory=list)
    intent_distribution: dict[str, int] = Field(default_factory=dict)
    total_estimated_volume: int = 0

    def add_query(self, query: Query):
        """Add a query and update statistics."""
        self.queries.append(query)
        intent_key = query.intent.value
        self.intent_distribution[intent_key] = self.intent_distribution.get(intent_key, 0) + 1
        if query.estimated_volume:
            self.total_estimated_volume += query.estimated_volume


# =============================================================================
# Step 5: Content Hub Models
# =============================================================================

class HubPage(BaseModel):
    """A page within a content hub."""
    id: str
    title: str
    page_type: str = Field(description="pillar, cluster, or supporting")
    target_queries: list[str] = Field(default_factory=list)
    target_intents: list[IntentType] = Field(default_factory=list)
    entity_ids: list[str] = Field(default_factory=list)
    recommended_format: str | None = None
    recommended_word_count: int | None = None
    schema_types: list[str] = Field(default_factory=list)
    internal_links_to: list[str] = Field(default_factory=list, description="Page IDs to link to")
    internal_links_from: list[str] = Field(default_factory=list, description="Page IDs linking here")
    existing_url: str | None = Field(default=None, description="URL if page exists")
    status: str = Field(default="planned", description="planned, exists, needs_update")
    priority: ContentPriority = ContentPriority.MEDIUM


class ContentHub(BaseModel):
    """A topical content hub with pillar and cluster structure."""
    id: str
    name: str
    primary_entity_id: str
    pillar_page: HubPage | None = None
    cluster_pages: list[HubPage] = Field(default_factory=list)
    supporting_pages: list[HubPage] = Field(default_factory=list)
    internal_link_count: int = 0
    coverage_score: float = Field(default=0.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)

    def all_pages(self) -> list[HubPage]:
        """Get all pages in the hub."""
        pages = []
        if self.pillar_page:
            pages.append(self.pillar_page)
        pages.extend(self.cluster_pages)
        pages.extend(self.supporting_pages)
        return pages

    def calculate_link_count(self):
        """Calculate total internal links in hub."""
        count = 0
        for page in self.all_pages():
            count += len(page.internal_links_to)
        self.internal_link_count = count
        return count


# =============================================================================
# Step 6: Content Specification Models
# =============================================================================

class Persona(BaseModel):
    """Target audience persona."""
    id: str
    name: str
    knowledge_level: str
    preferred_formats: list[str] = Field(default_factory=list)
    content_tone: str
    motivations: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    query_modifiers: list[str] = Field(default_factory=list, description="Terms this persona uses")


class ContentSpec(BaseModel):
    """Detailed content specification for a page."""
    page_id: str
    title: str
    target_url: str | None = None
    primary_query: str
    secondary_queries: list[str] = Field(default_factory=list)
    target_personas: list[str] = Field(default_factory=list)
    recommended_format: str
    content_structure: list[str] = Field(
        default_factory=list,
        description="Recommended H2/H3 sections"
    )
    schema_markup: list[dict[str, Any]] = Field(default_factory=list)
    ai_optimization_notes: list[str] = Field(
        default_factory=list,
        description="Specific tips for AI extractability"
    )
    serp_feature_targets: list[str] = Field(default_factory=list)
    internal_link_anchors: dict[str, str] = Field(
        default_factory=dict,
        description="Anchor text -> target page ID"
    )
    word_count_target: int | None = None
    content_tone: str | None = None
    priority: ContentPriority = ContentPriority.MEDIUM
    estimated_impact: str | None = Field(default=None, description="Expected visibility impact")


# =============================================================================
# Step 7: Measurement Models
# =============================================================================

class KPI(BaseModel):
    """Key Performance Indicator for tracking."""
    id: str
    name: str
    description: str
    measurement_method: str
    refresh_cadence: str
    priority: str
    current_value: float | None = None
    target_value: float | None = None
    baseline_value: float | None = None
    last_measured: datetime | None = None


class ContentAuditItem(BaseModel):
    """Item in content freshness audit."""
    page_id: str
    url: str
    title: str
    last_updated: datetime | None = None
    freshness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    update_priority: ContentPriority = ContentPriority.MEDIUM
    recommended_updates: list[str] = Field(default_factory=list)


class MeasurementPlan(BaseModel):
    """Complete measurement and iteration framework."""
    brand_name: str
    kpis: list[KPI] = Field(default_factory=list)
    content_audit: list[ContentAuditItem] = Field(default_factory=list)
    ai_monitoring_queries: list[str] = Field(
        default_factory=list,
        description="Queries to monitor in AI systems"
    )
    refresh_schedule: dict[str, str] = Field(
        default_factory=dict,
        description="Content type -> refresh cadence"
    )
    competitor_tracking: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


# =============================================================================
# Complete Framework Output
# =============================================================================

class FrameworkOutput(BaseModel):
    """Complete output of the AI Search Visibility Framework."""
    brand_name: str
    primary_niche: str
    generated_at: datetime = Field(default_factory=datetime.now)
    version: str = Field(default="1.0")

    # Step 1
    ontology: Ontology | None = None

    # Step 2 (entity expansion embedded in ontology)

    # Step 3
    taxonomy: Taxonomy | None = None

    # Step 4
    query_clusters: list[QueryCluster] = Field(default_factory=list)

    # Step 5
    content_hubs: list[ContentHub] = Field(default_factory=list)

    # Step 6
    personas: list[Persona] = Field(default_factory=list)
    content_specs: list[ContentSpec] = Field(default_factory=list)

    # Step 7
    measurement_plan: MeasurementPlan | None = None

    # Summary statistics
    summary: dict[str, Any] = Field(default_factory=dict)

    def generate_summary(self):
        """Generate summary statistics."""
        self.summary = {
            "total_entities": len(self.ontology.entities) if self.ontology else 0,
            "total_relationships": len(self.ontology.relationships) if self.ontology else 0,
            "taxonomy_nodes": len(self.taxonomy.nodes) if self.taxonomy else 0,
            "query_clusters": len(self.query_clusters),
            "total_queries": sum(len(qc.queries) for qc in self.query_clusters),
            "content_hubs": len(self.content_hubs),
            "total_pages_planned": sum(len(hub.all_pages()) for hub in self.content_hubs),
            "content_specs": len(self.content_specs),
            "kpis_defined": len(self.measurement_plan.kpis) if self.measurement_plan else 0,
        }
        return self.summary
