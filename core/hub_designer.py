"""
Step 5: Topical Hub Designer

Plans pillar + cluster content structure with internal linking
graphs for comprehensive topic coverage.
"""

import hashlib
from typing import Any

from config.templates import DEFAULT_CONTENT_FORMATS
from utils.data_models import (
    Entity,
    Ontology,
    Taxonomy,
    QueryCluster,
    ContentHub,
    HubPage,
    IntentType,
    ContentPriority,
)


class HubDesigner:
    """
    Design topical content hubs with pillar-cluster architecture.

    Creates:
    - Pillar pages (comprehensive topic coverage)
    - Cluster pages (specific subtopics)
    - Supporting pages (related content)
    - Internal linking graph
    """

    # Word count recommendations by page type
    WORD_COUNT_TARGETS = {
        "pillar": 3000,
        "cluster": 1500,
        "supporting": 800,
    }

    def __init__(
        self,
        ontology: Ontology,
        taxonomy: Taxonomy,
        query_clusters: list[QueryCluster],
    ):
        self.ontology = ontology
        self.taxonomy = taxonomy
        self.query_clusters = query_clusters
        self.query_map = {qc.primary_entity_id: qc for qc in query_clusters}
        self.hubs: list[ContentHub] = []

    def design_all_hubs(self) -> list[ContentHub]:
        """
        Design content hubs for all major entities.

        Returns:
            List of designed content hubs
        """
        # Create hubs for level-1 taxonomy nodes (main categories)
        for node in self.taxonomy.nodes:
            if node.level != 1:
                continue

            if not node.entity_ids:
                continue

            primary_entity_id = node.entity_ids[0]
            entity = self.ontology.get_entity(primary_entity_id)

            if not entity:
                continue

            hub = self._design_hub(entity, node.id)
            self.hubs.append(hub)

        # Map internal links between hubs
        self._map_hub_links()

        # Calculate coverage scores
        for hub in self.hubs:
            hub.coverage_score = self._calculate_coverage(hub)

        return self.hubs

    def _design_hub(self, entity: Entity, taxonomy_node_id: str) -> ContentHub:
        """Design a content hub for an entity."""
        hub_id = f"hub_{hashlib.md5(entity.id.encode()).hexdigest()[:8]}"

        hub = ContentHub(
            id=hub_id,
            name=entity.name,
            primary_entity_id=entity.id,
        )

        # Create pillar page
        hub.pillar_page = self._create_pillar_page(entity, hub_id)

        # Create cluster pages from query clusters
        query_cluster = self.query_map.get(entity.id)
        if query_cluster:
            hub.cluster_pages = self._create_cluster_pages(
                entity, query_cluster, hub_id
            )

        # Create supporting pages from related entities
        hub.supporting_pages = self._create_supporting_pages(entity, hub_id)

        # Map internal links within hub
        self._map_internal_links(hub)

        # Calculate link count
        hub.calculate_link_count()

        return hub

    def _create_pillar_page(self, entity: Entity, hub_id: str) -> HubPage:
        """Create the pillar page for a hub."""
        page_id = f"{hub_id}_pillar"

        # Get queries for this entity
        query_cluster = self.query_map.get(entity.id)
        target_queries = []
        if query_cluster:
            # Use high-priority queries
            high_priority = [
                q for q in query_cluster.queries
                if q.priority in [ContentPriority.CRITICAL, ContentPriority.HIGH]
            ]
            target_queries = [q.query_text for q in high_priority[:5]]

        return HubPage(
            id=page_id,
            title=f"Complete Guide to {entity.name}",
            page_type="pillar",
            target_queries=target_queries,
            target_intents=[IntentType.INFORMATIONAL],
            entity_ids=[entity.id],
            recommended_format="long_form_guide",
            recommended_word_count=self.WORD_COUNT_TARGETS["pillar"],
            schema_types=["Article", "BreadcrumbList", "FAQPage"],
            priority=ContentPriority.CRITICAL,
            status="planned",
        )

    def _create_cluster_pages(
        self,
        entity: Entity,
        query_cluster: QueryCluster,
        hub_id: str,
    ) -> list[HubPage]:
        """Create cluster pages based on query patterns."""
        cluster_pages = []

        # Group queries by fanout pattern
        by_pattern: dict[str, list] = {}
        for query in query_cluster.queries:
            pattern = query.fanout_pattern or "general"
            if pattern not in by_pattern:
                by_pattern[pattern] = []
            by_pattern[pattern].append(query)

        # Create a cluster page for each significant pattern
        for pattern, queries in by_pattern.items():
            if len(queries) < 2:
                continue

            page_id = f"{hub_id}_cluster_{pattern}"

            # Determine page characteristics based on pattern
            title, format_type, intents = self._get_pattern_config(
                pattern, entity.name
            )

            # Get schema types for this format
            format_config = DEFAULT_CONTENT_FORMATS.get(format_type, {})
            schema_types = format_config.get("schema_types", ["Article"])

            # Determine priority based on query priorities
            has_critical = any(q.priority == ContentPriority.CRITICAL for q in queries)
            has_high = any(q.priority == ContentPriority.HIGH for q in queries)
            priority = (
                ContentPriority.CRITICAL if has_critical
                else ContentPriority.HIGH if has_high
                else ContentPriority.MEDIUM
            )

            cluster_pages.append(HubPage(
                id=page_id,
                title=title,
                page_type="cluster",
                target_queries=[q.query_text for q in queries[:5]],
                target_intents=intents,
                entity_ids=[entity.id],
                recommended_format=format_type,
                recommended_word_count=self.WORD_COUNT_TARGETS["cluster"],
                schema_types=schema_types,
                priority=priority,
                status="planned",
            ))

        return cluster_pages[:10]  # Limit cluster pages per hub

    def _get_pattern_config(
        self,
        pattern: str,
        entity_name: str,
    ) -> tuple[str, str, list[IntentType]]:
        """Get title, format, and intents for a pattern."""
        configs = {
            "definitional": (
                f"What is {entity_name}? Complete Overview",
                "glossary_definition",
                [IntentType.INFORMATIONAL],
            ),
            "how_to": (
                f"How to Use {entity_name}: Step-by-Step Guide",
                "how_to_tutorial",
                [IntentType.INFORMATIONAL],
            ),
            "comparison": (
                f"{entity_name} Alternatives & Comparisons",
                "comparison_table",
                [IntentType.COMMERCIAL],
            ),
            "problems": (
                f"Common {entity_name} Problems & Solutions",
                "faq_page",
                [IntentType.INFORMATIONAL],
            ),
            "benefits": (
                f"Benefits of {entity_name}: Why Use It?",
                "listicle",
                [IntentType.COMMERCIAL],
            ),
            "examples": (
                f"{entity_name} Examples & Use Cases",
                "case_study",
                [IntentType.INFORMATIONAL],
            ),
            "pricing": (
                f"{entity_name} Pricing & Plans",
                "comparison_table",
                [IntentType.TRANSACTIONAL, IntentType.COMMERCIAL],
            ),
            "reviews": (
                f"{entity_name} Review: Pros, Cons & Verdict",
                "product_review",
                [IntentType.COMMERCIAL],
            ),
            "integration": (
                f"{entity_name} Integrations & APIs",
                "how_to_tutorial",
                [IntentType.INFORMATIONAL],
            ),
            "advanced": (
                f"Advanced {entity_name} Tips & Best Practices",
                "long_form_guide",
                [IntentType.INFORMATIONAL],
            ),
        }

        return configs.get(
            pattern,
            (f"{entity_name}: {pattern.title()}", "long_form_guide", [IntentType.INFORMATIONAL]),
        )

    def _create_supporting_pages(
        self,
        entity: Entity,
        hub_id: str,
    ) -> list[HubPage]:
        """Create supporting pages from related entities."""
        supporting_pages = []

        # Get related entities
        related = self.ontology.get_related_entities(entity.id)

        for related_entity, relationship in related[:5]:
            # Skip competitors
            if related_entity.type.value == "competitor":
                continue

            page_id = f"{hub_id}_support_{hashlib.md5(related_entity.id.encode()).hexdigest()[:6]}"

            # Title based on relationship
            rel_type = relationship.relationship_type.value
            if rel_type == "is_a":
                title = f"{related_entity.name}: A Type of {entity.name}"
            elif rel_type == "part_of":
                title = f"{related_entity.name} in {entity.name}"
            elif rel_type == "used_for":
                title = f"Using {entity.name} for {related_entity.name}"
            else:
                title = f"{related_entity.name} & {entity.name}"

            supporting_pages.append(HubPage(
                id=page_id,
                title=title,
                page_type="supporting",
                target_queries=[],
                target_intents=[IntentType.INFORMATIONAL],
                entity_ids=[entity.id, related_entity.id],
                recommended_format="long_form_guide",
                recommended_word_count=self.WORD_COUNT_TARGETS["supporting"],
                schema_types=["Article"],
                priority=ContentPriority.LOW,
                status="planned",
            ))

        return supporting_pages

    def _map_internal_links(self, hub: ContentHub):
        """Map internal links within a hub."""
        all_pages = hub.all_pages()

        if not hub.pillar_page:
            return

        pillar_id = hub.pillar_page.id

        for page in all_pages:
            if page.id == pillar_id:
                # Pillar links to all clusters
                page.internal_links_to = [p.id for p in hub.cluster_pages]
                page.internal_links_from = []
            elif page.page_type == "cluster":
                # Clusters link to pillar and related clusters
                page.internal_links_to = [pillar_id]
                page.internal_links_from = [pillar_id]
                # Link to 2 other clusters
                other_clusters = [
                    p.id for p in hub.cluster_pages
                    if p.id != page.id
                ][:2]
                page.internal_links_to.extend(other_clusters)
            else:
                # Supporting pages link to pillar
                page.internal_links_to = [pillar_id]
                page.internal_links_from = []

    def _map_hub_links(self):
        """Map links between hubs."""
        # Link related hubs based on entity relationships
        for hub in self.hubs:
            entity = self.ontology.get_entity(hub.primary_entity_id)
            if not entity:
                continue

            related = self.ontology.get_related_entities(entity.id)

            for related_entity, _ in related:
                # Find hub for related entity
                for other_hub in self.hubs:
                    if other_hub.primary_entity_id == related_entity.id:
                        # Link pillars
                        if hub.pillar_page and other_hub.pillar_page:
                            if other_hub.pillar_page.id not in hub.pillar_page.internal_links_to:
                                hub.pillar_page.internal_links_to.append(
                                    other_hub.pillar_page.id
                                )
                        break

    def _calculate_coverage(self, hub: ContentHub) -> float:
        """Calculate coverage score for a hub."""
        scores = []

        # Query coverage
        query_cluster = self.query_map.get(hub.primary_entity_id)
        if query_cluster:
            total_queries = len(query_cluster.queries)
            covered_queries = sum(
                len(p.target_queries) for p in hub.all_pages()
            )
            query_coverage = min(1.0, covered_queries / max(total_queries, 1))
            scores.append(query_coverage)

        # Intent coverage
        all_intents = set(IntentType)
        covered_intents = set()
        for page in hub.all_pages():
            covered_intents.update(page.target_intents)
        intent_coverage = len(covered_intents) / len(all_intents)
        scores.append(intent_coverage)

        # Link density
        total_links = hub.internal_link_count
        expected_links = len(hub.all_pages()) * 3
        link_coverage = min(1.0, total_links / max(expected_links, 1))
        scores.append(link_coverage)

        return sum(scores) / len(scores) if scores else 0.0

    def get_hub_visualization_data(self, hub: ContentHub) -> dict[str, Any]:
        """Get hub data formatted for visualization."""
        nodes = []
        edges = []

        for page in hub.all_pages():
            nodes.append({
                "id": page.id,
                "label": page.title[:30] + "..." if len(page.title) > 30 else page.title,
                "type": page.page_type,
                "size": {
                    "pillar": 40,
                    "cluster": 25,
                    "supporting": 15,
                }.get(page.page_type, 20),
                "color": {
                    "pillar": "#4CAF50",
                    "cluster": "#2196F3",
                    "supporting": "#FF9800",
                }.get(page.page_type, "#9E9E9E"),
            })

            for target_id in page.internal_links_to:
                edges.append({
                    "source": page.id,
                    "target": target_id,
                })

        return {"nodes": nodes, "edges": edges}

    def suggest_content_gaps(self) -> list[dict[str, Any]]:
        """Identify content gaps across all hubs."""
        gaps = []

        for hub in self.hubs:
            # Check intent coverage
            covered_intents = set()
            for page in hub.all_pages():
                covered_intents.update(page.target_intents)

            missing_intents = set(IntentType) - covered_intents

            for intent in missing_intents:
                gaps.append({
                    "hub_name": hub.name,
                    "gap_type": "missing_intent",
                    "intent": intent.value,
                    "recommendation": f"Create content targeting {intent.value} intent for {hub.name}",
                    "priority": "high" if intent in [IntentType.COMMERCIAL, IntentType.TRANSACTIONAL] else "medium",
                })

            # Check for thin hubs
            if len(hub.cluster_pages) < 3:
                gaps.append({
                    "hub_name": hub.name,
                    "gap_type": "thin_hub",
                    "cluster_count": len(hub.cluster_pages),
                    "recommendation": f"Expand {hub.name} hub with more cluster content",
                    "priority": "medium",
                })

        return sorted(gaps, key=lambda x: x.get("priority", "low") == "high", reverse=True)

    def generate_hub_report(self) -> dict[str, Any]:
        """Generate comprehensive hub design report."""
        total_pages = sum(len(h.all_pages()) for h in self.hubs)
        total_links = sum(h.internal_link_count for h in self.hubs)

        page_type_counts = {"pillar": 0, "cluster": 0, "supporting": 0}
        for hub in self.hubs:
            if hub.pillar_page:
                page_type_counts["pillar"] += 1
            page_type_counts["cluster"] += len(hub.cluster_pages)
            page_type_counts["supporting"] += len(hub.supporting_pages)

        return {
            "total_hubs": len(self.hubs),
            "total_pages": total_pages,
            "total_internal_links": total_links,
            "avg_pages_per_hub": total_pages / len(self.hubs) if self.hubs else 0,
            "avg_links_per_hub": total_links / len(self.hubs) if self.hubs else 0,
            "page_type_distribution": page_type_counts,
            "coverage_scores": {
                hub.name: round(hub.coverage_score, 2) for hub in self.hubs
            },
            "content_gaps": self.suggest_content_gaps()[:10],
            "hub_details": [
                {
                    "name": hub.name,
                    "pillar": hub.pillar_page.title if hub.pillar_page else None,
                    "cluster_count": len(hub.cluster_pages),
                    "supporting_count": len(hub.supporting_pages),
                    "link_count": hub.internal_link_count,
                    "coverage": round(hub.coverage_score, 2),
                }
                for hub in self.hubs
            ],
        }
