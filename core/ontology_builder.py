"""
Step 1: Ontology Builder

Extracts entities from source data and maps semantic relationships
to create a comprehensive brand ontology.
"""

import re
import hashlib
from typing import Any

from config.templates import (
    BrandFoundationConfig,
    DEFAULT_RELATIONSHIP_TYPES,
    SourceMode,
)
from utils.data_models import (
    Entity,
    EntityType,
    Relationship,
    RelationshipType,
    Ontology,
)
from utils.sitemap_parser import SitemapParser


class OntologyBuilder:
    """
    Build brand ontology from seed entities or sitemap extraction.

    The ontology captures:
    - Core entities (products, services, concepts)
    - Supporting entities (attributes, contexts)
    - Semantic relationships between entities
    """

    def __init__(self, config: BrandFoundationConfig):
        self.config = config
        self.entities: dict[str, Entity] = {}
        self.relationships: list[Relationship] = []

    def build(self) -> Ontology:
        """
        Build complete ontology based on configuration.

        Returns:
            Ontology with entities and relationships
        """
        # Extract entities based on source mode
        if self.config.source_mode == SourceMode.SITEMAP:
            self._extract_from_sitemap()
        elif self.config.source_mode == SourceMode.SEED:
            self._create_from_seeds()
        else:  # HYBRID
            self._create_from_seeds()
            if self.config.sitemap_url:
                self._extract_from_sitemap()

        # Add brand as root entity
        self._add_brand_entity()

        # Infer relationships between entities
        self._infer_relationships()

        # Calculate entity scores
        self._calculate_entity_scores()

        return Ontology(
            brand_name=self.config.brand_name,
            entities=list(self.entities.values()),
            relationships=self.relationships,
        )

    def _generate_entity_id(self, name: str) -> str:
        """Generate unique entity ID from name."""
        normalized = name.lower().strip()
        hash_suffix = hashlib.md5(normalized.encode()).hexdigest()[:8]
        slug = re.sub(r"[^a-z0-9]+", "_", normalized)[:30]
        return f"{slug}_{hash_suffix}"

    def _add_brand_entity(self):
        """Add brand as the root entity."""
        brand_id = self._generate_entity_id(self.config.brand_name)
        self.entities[brand_id] = Entity(
            id=brand_id,
            name=self.config.brand_name,
            type=EntityType.CORE,
            description=f"Primary brand entity for {self.config.brand_name}",
            attributes={
                "niche": self.config.primary_niche,
                "goals": [g.value for g in self.config.business_goals],
            },
            commercial_value=1.0,
            semantic_centrality=1.0,
        )

    def _create_from_seeds(self):
        """Create entities from seed list."""
        for seed in self.config.seed_entities:
            seed = seed.strip()
            if not seed:
                continue

            entity_id = self._generate_entity_id(seed)
            if entity_id not in self.entities:
                self.entities[entity_id] = Entity(
                    id=entity_id,
                    name=seed,
                    type=EntityType.CORE,
                    description=None,
                    aliases=self._generate_aliases(seed),
                )

        # Add competitors as competitor entities
        for competitor in self.config.competitors:
            competitor = competitor.strip()
            if not competitor:
                continue

            entity_id = self._generate_entity_id(competitor)
            if entity_id not in self.entities:
                self.entities[entity_id] = Entity(
                    id=entity_id,
                    name=competitor,
                    type=EntityType.COMPETITOR,
                    description=f"Competitor: {competitor}",
                )

    def _extract_from_sitemap(self):
        """Extract entities from sitemap analysis."""
        if not self.config.sitemap_url:
            return

        try:
            with SitemapParser() as parser:
                extracted = parser.extract_entities_from_sitemap(self.config.sitemap_url)

                for item in extracted[:50]:  # Limit entities
                    name = item["name"]
                    entity_id = self._generate_entity_id(name)

                    if entity_id not in self.entities:
                        self.entities[entity_id] = Entity(
                            id=entity_id,
                            name=name,
                            type=EntityType.CORE if item["frequency"] > 1 else EntityType.SUPPORTING,
                            source_urls=item.get("source_urls", []),
                            attributes={
                                "frequency": item["frequency"],
                                "categories": item.get("categories", []),
                            },
                        )
                    else:
                        # Update existing entity with sitemap data
                        existing = self.entities[entity_id]
                        existing.source_urls.extend(item.get("source_urls", []))

        except Exception as e:
            # Log error but continue - sitemap extraction is optional
            print(f"Warning: Could not extract from sitemap: {e}")

    def _generate_aliases(self, entity_name: str) -> list[str]:
        """Generate common aliases for an entity."""
        aliases = []
        name = entity_name.strip()

        # Plural/singular variations
        if name.endswith("s") and len(name) > 3:
            aliases.append(name[:-1])  # Remove 's'
        elif not name.endswith("s"):
            aliases.append(name + "s")  # Add 's'

        # Common abbreviations (if multi-word)
        words = name.split()
        if len(words) > 1:
            # Acronym
            acronym = "".join(w[0].upper() for w in words)
            if len(acronym) >= 2:
                aliases.append(acronym)

        # Hyphenated/spaced variations
        if "-" in name:
            aliases.append(name.replace("-", " "))
        elif " " in name:
            aliases.append(name.replace(" ", "-"))

        return aliases

    def _infer_relationships(self):
        """Infer semantic relationships between entities."""
        entity_list = list(self.entities.values())
        brand_id = self._generate_entity_id(self.config.brand_name)

        for entity in entity_list:
            if entity.id == brand_id:
                continue

            # Connect all core entities to brand
            if entity.type == EntityType.CORE:
                self.relationships.append(Relationship(
                    source_id=entity.id,
                    target_id=brand_id,
                    relationship_type=RelationshipType.PART_OF,
                    weight=0.8,
                    context="Core entity of brand",
                ))

            # Connect competitors with alternative_to relationship
            if entity.type == EntityType.COMPETITOR:
                self.relationships.append(Relationship(
                    source_id=entity.id,
                    target_id=brand_id,
                    relationship_type=RelationshipType.ALTERNATIVE_TO,
                    weight=0.6,
                    bidirectional=True,
                    context="Competitor relationship",
                ))

        # Infer relationships between entities based on name similarity
        for i, entity1 in enumerate(entity_list):
            for entity2 in entity_list[i + 1:]:
                relationship = self._detect_relationship(entity1, entity2)
                if relationship:
                    self.relationships.append(relationship)

    def _detect_relationship(self, e1: Entity, e2: Entity) -> Relationship | None:
        """Detect potential relationship between two entities."""
        name1 = e1.name.lower()
        name2 = e2.name.lower()

        # Check if one contains the other (potential is_a or part_of)
        if name1 in name2 and name1 != name2:
            return Relationship(
                source_id=e2.id,
                target_id=e1.id,
                relationship_type=RelationshipType.IS_A,
                weight=0.7,
                context=f"'{e2.name}' contains '{e1.name}'",
            )
        elif name2 in name1 and name1 != name2:
            return Relationship(
                source_id=e1.id,
                target_id=e2.id,
                relationship_type=RelationshipType.IS_A,
                weight=0.7,
                context=f"'{e1.name}' contains '{e2.name}'",
            )

        # Check for word overlap (relates_to)
        words1 = set(name1.split())
        words2 = set(name2.split())
        common = words1 & words2 - {"the", "a", "an", "and", "or", "for", "of", "in"}

        if common and len(common) >= 1:
            return Relationship(
                source_id=e1.id,
                target_id=e2.id,
                relationship_type=RelationshipType.RELATES_TO,
                weight=0.5,
                bidirectional=True,
                context=f"Shared terms: {', '.join(common)}",
            )

        return None

    def _calculate_entity_scores(self):
        """Calculate commercial value and semantic centrality for entities."""
        # Count relationships per entity
        relationship_counts: dict[str, int] = {}
        for rel in self.relationships:
            relationship_counts[rel.source_id] = relationship_counts.get(rel.source_id, 0) + 1
            relationship_counts[rel.target_id] = relationship_counts.get(rel.target_id, 0) + 1

        # Calculate scores
        max_rels = max(relationship_counts.values()) if relationship_counts else 1

        for entity_id, entity in self.entities.items():
            rel_count = relationship_counts.get(entity_id, 0)

            # Semantic centrality based on relationship count
            entity.semantic_centrality = min(1.0, rel_count / max_rels + 0.2)

            # Commercial value based on entity type
            if entity.type == EntityType.CORE:
                entity.commercial_value = 0.8
            elif entity.type == EntityType.SUPPORTING:
                entity.commercial_value = 0.4
            elif entity.type == EntityType.COMPETITOR:
                entity.commercial_value = 0.3
            else:
                entity.commercial_value = 0.5

    def add_entity(
        self,
        name: str,
        entity_type: EntityType = EntityType.CORE,
        description: str | None = None,
        aliases: list[str] | None = None,
    ) -> Entity:
        """Manually add an entity to the ontology."""
        entity_id = self._generate_entity_id(name)

        entity = Entity(
            id=entity_id,
            name=name,
            type=entity_type,
            description=description,
            aliases=aliases or self._generate_aliases(name),
        )

        self.entities[entity_id] = entity
        return entity

    def add_relationship(
        self,
        source_name: str,
        target_name: str,
        rel_type: RelationshipType,
        weight: float = 1.0,
        bidirectional: bool = False,
    ) -> Relationship | None:
        """Manually add a relationship between entities."""
        source_id = self._generate_entity_id(source_name)
        target_id = self._generate_entity_id(target_name)

        if source_id not in self.entities or target_id not in self.entities:
            return None

        rel = Relationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=rel_type,
            weight=weight,
            bidirectional=bidirectional,
        )

        self.relationships.append(rel)
        return rel

    def get_entity_graph_data(self) -> dict[str, Any]:
        """
        Get ontology data formatted for graph visualization.

        Returns data suitable for networkx or similar graph libraries.
        """
        nodes = []
        edges = []

        for entity in self.entities.values():
            nodes.append({
                "id": entity.id,
                "label": entity.name,
                "type": entity.type.value,
                "size": entity.semantic_centrality * 30 + 10,
                "color": self._get_entity_color(entity.type),
            })

        for rel in self.relationships:
            edges.append({
                "source": rel.source_id,
                "target": rel.target_id,
                "label": rel.relationship_type.value,
                "weight": rel.weight,
            })

        return {"nodes": nodes, "edges": edges}

    def _get_entity_color(self, entity_type: EntityType) -> str:
        """Get color for entity type."""
        colors = {
            EntityType.CORE: "#4CAF50",
            EntityType.SUPPORTING: "#2196F3",
            EntityType.COMPETITOR: "#f44336",
            EntityType.ATTRIBUTE: "#FF9800",
        }
        return colors.get(entity_type, "#9E9E9E")
