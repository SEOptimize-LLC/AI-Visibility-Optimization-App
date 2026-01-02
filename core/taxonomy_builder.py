"""
Step 3: Taxonomy Builder

Creates hierarchical category structures with cross-cutting facets
and internal linking maps for navigation optimization.
"""

import hashlib
import re
from typing import Any

from utils.data_models import (
    Entity,
    EntityType,
    Ontology,
    TaxonomyNode,
    Taxonomy,
    RelationshipType,
)


class TaxonomyBuilder:
    """
    Build optimized taxonomy structure from ontology.

    Creates:
    - Hierarchical categories (tree structure)
    - Cross-cutting facets (tag-like classifications)
    - Internal linking map (category page connections)
    """

    def __init__(self, ontology: Ontology, primary_niche: str):
        self.ontology = ontology
        self.primary_niche = primary_niche
        self.nodes: dict[str, TaxonomyNode] = {}
        self.facets: dict[str, set[str]] = {}

    def build(self) -> Taxonomy:
        """
        Build complete taxonomy from ontology.

        Returns:
            Taxonomy with nodes and facet definitions
        """
        # Create root node based on niche
        self._create_root_node()

        # Create category nodes from core entities
        self._create_category_nodes()

        # Create subcategory nodes from relationships
        self._create_subcategory_nodes()

        # Generate facets from entity attributes
        self._generate_facets()

        # Map internal links
        self._map_internal_links()

        # Generate SEO metadata
        self._generate_seo_metadata()

        return Taxonomy(
            brand_name=self.ontology.brand_name,
            nodes=list(self.nodes.values()),
            facet_definitions={k: list(v) for k, v in self.facets.items()},
        )

    def _generate_node_id(self, name: str) -> str:
        """Generate unique node ID."""
        normalized = name.lower().strip()
        hash_suffix = hashlib.md5(normalized.encode()).hexdigest()[:6]
        slug = re.sub(r"[^a-z0-9]+", "_", normalized)[:20]
        return f"tax_{slug}_{hash_suffix}"

    def _create_root_node(self):
        """Create root taxonomy node based on niche."""
        root_id = self._generate_node_id(self.primary_niche)
        self.nodes[root_id] = TaxonomyNode(
            id=root_id,
            name=self.primary_niche,
            parent_id=None,
            level=0,
            seo_title=f"{self.primary_niche} - Complete Guide | {self.ontology.brand_name}",
            seo_description=f"Comprehensive resource for {self.primary_niche}. Expert guides, tutorials, and insights from {self.ontology.brand_name}.",
        )

    def _create_category_nodes(self):
        """Create category nodes from core entities."""
        # Get core entities sorted by centrality
        core_entities = [
            e for e in self.ontology.entities
            if e.type == EntityType.CORE
        ]
        core_entities.sort(key=lambda x: x.semantic_centrality, reverse=True)

        # Get root node ID
        root_id = list(self.nodes.keys())[0]

        # Create category node for each core entity
        for entity in core_entities[:15]:  # Limit top-level categories
            node_id = self._generate_node_id(entity.name)
            self.nodes[node_id] = TaxonomyNode(
                id=node_id,
                name=entity.name,
                parent_id=root_id,
                entity_ids=[entity.id],
                level=1,
                target_url=self._generate_url_slug(entity.name),
            )

    def _create_subcategory_nodes(self):
        """Create subcategory nodes from relationships."""
        # For each category, find related entities to create subcategories
        category_nodes = [n for n in self.nodes.values() if n.level == 1]

        for cat_node in category_nodes:
            if not cat_node.entity_ids:
                continue

            primary_entity_id = cat_node.entity_ids[0]
            related = self.ontology.get_related_entities(primary_entity_id)

            # Create subcategories from related entities
            for related_entity, relationship in related[:5]:  # Limit subcategories
                # Skip competitors
                if related_entity.type == EntityType.COMPETITOR:
                    continue

                # Skip if already has a category
                existing_node = self._find_node_for_entity(related_entity.id)
                if existing_node:
                    continue

                node_id = self._generate_node_id(related_entity.name)
                self.nodes[node_id] = TaxonomyNode(
                    id=node_id,
                    name=related_entity.name,
                    parent_id=cat_node.id,
                    entity_ids=[related_entity.id],
                    level=2,
                    target_url=self._generate_url_slug(
                        f"{cat_node.name}/{related_entity.name}"
                    ),
                )

    def _find_node_for_entity(self, entity_id: str) -> TaxonomyNode | None:
        """Find existing taxonomy node containing an entity."""
        for node in self.nodes.values():
            if entity_id in node.entity_ids:
                return node
        return None

    def _generate_facets(self):
        """Generate cross-cutting facets from entity attributes."""
        # Intent-based facets
        self.facets["intent"] = {
            "learn",
            "compare",
            "implement",
            "troubleshoot",
            "purchase",
        }

        # Audience-based facets
        self.facets["audience"] = {
            "beginners",
            "intermediate",
            "advanced",
            "decision-makers",
        }

        # Content type facets
        self.facets["content_type"] = {
            "guides",
            "tutorials",
            "comparisons",
            "reviews",
            "case-studies",
            "tools",
        }

        # Extract facets from entity attributes
        for entity in self.ontology.entities:
            if "categories" in entity.attributes:
                cats = entity.attributes["categories"]
                if isinstance(cats, list):
                    if "category" not in self.facets:
                        self.facets["category"] = set()
                    self.facets["category"].update(cats)

        # Assign facets to nodes based on entity characteristics
        for node in self.nodes.values():
            if node.level == 0:
                continue

            # Assign default facets based on node level
            if node.level == 1:
                node.facets = ["guides", "tutorials"]
            else:
                node.facets = ["tutorials"]

    def _map_internal_links(self):
        """Map internal linking structure between nodes."""
        nodes_by_level = {}
        for node in self.nodes.values():
            if node.level not in nodes_by_level:
                nodes_by_level[node.level] = []
            nodes_by_level[node.level].append(node)

        for node in self.nodes.values():
            links = []

            # Link to parent
            if node.parent_id:
                links.append(node.parent_id)

            # Link to siblings (same level, same parent)
            siblings = [
                n.id for n in self.nodes.values()
                if n.parent_id == node.parent_id and n.id != node.id
            ]
            links.extend(siblings[:3])  # Limit sibling links

            # Link to children
            children = [
                n.id for n in self.nodes.values()
                if n.parent_id == node.id
            ]
            links.extend(children)

            # Link to related nodes via entity relationships
            if node.entity_ids:
                for entity_id in node.entity_ids:
                    related = self.ontology.get_related_entities(entity_id)
                    for related_entity, _ in related[:3]:
                        related_node = self._find_node_for_entity(related_entity.id)
                        if related_node and related_node.id not in links:
                            links.append(related_node.id)

            node.internal_links_to = list(dict.fromkeys(links))[:10]  # Dedupe and limit

    def _generate_seo_metadata(self):
        """Generate SEO titles and descriptions for nodes."""
        for node in self.nodes.values():
            if not node.seo_title:
                if node.level == 1:
                    node.seo_title = f"{node.name} Guide - Expert Resources | {self.ontology.brand_name}"
                else:
                    parent = self.nodes.get(node.parent_id or "")
                    parent_name = parent.name if parent else self.primary_niche
                    node.seo_title = f"{node.name} - {parent_name} | {self.ontology.brand_name}"

            if not node.seo_description:
                node.seo_description = f"Learn about {node.name.lower()} with our comprehensive guides. Expert tips, tutorials, and resources from {self.ontology.brand_name}."

    def _generate_url_slug(self, name: str) -> str:
        """Generate URL slug from name."""
        slug = name.lower()
        slug = re.sub(r"[^a-z0-9\s/]", "", slug)
        slug = re.sub(r"\s+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return f"/{slug.strip('-')}/"

    def get_taxonomy_tree(self) -> dict[str, Any]:
        """
        Get taxonomy as a tree structure for visualization.

        Returns nested dictionary representing the taxonomy tree.
        """
        def build_subtree(parent_id: str | None) -> list[dict[str, Any]]:
            children = [n for n in self.nodes.values() if n.parent_id == parent_id]
            return [
                {
                    "id": node.id,
                    "name": node.name,
                    "level": node.level,
                    "url": node.target_url,
                    "children": build_subtree(node.id),
                    "link_count": len(node.internal_links_to),
                }
                for node in sorted(children, key=lambda x: x.name)
            ]

        return {
            "brand": self.ontology.brand_name,
            "tree": build_subtree(None),
        }

    def get_link_map(self) -> dict[str, list[str]]:
        """
        Get internal link map.

        Returns dict mapping node IDs to their link targets.
        """
        return {
            node.id: node.internal_links_to
            for node in self.nodes.values()
        }

    def get_navigation_paths(self, target_node_id: str) -> list[list[str]]:
        """
        Get all navigation paths to a target node.

        Returns list of paths (each path is list of node names).
        """
        paths = []
        target = self.nodes.get(target_node_id)

        if not target:
            return paths

        # Primary path (through hierarchy)
        primary_path = []
        current = target
        while current:
            primary_path.insert(0, current.name)
            current = self.nodes.get(current.parent_id or "")
        paths.append(primary_path)

        # Alternative paths through internal links
        for node in self.nodes.values():
            if target_node_id in node.internal_links_to and node.id != target.parent_id:
                alt_path = [node.name, target.name]
                paths.append(alt_path)

        return paths[:5]  # Limit paths

    def suggest_new_categories(self) -> list[dict[str, str]]:
        """
        Suggest new categories based on uncategorized entities.

        Returns list of suggestions with entity info.
        """
        suggestions = []

        # Find entities not in any taxonomy node
        categorized = set()
        for node in self.nodes.values():
            categorized.update(node.entity_ids)

        for entity in self.ontology.entities:
            if entity.id not in categorized and entity.type != EntityType.COMPETITOR:
                # Find best parent
                best_parent = None
                best_score = 0

                for node in self.nodes.values():
                    if node.level != 1:
                        continue

                    # Score based on relationships
                    for node_entity_id in node.entity_ids:
                        related_ids = [
                            e.id for e, _ in
                            self.ontology.get_related_entities(node_entity_id)
                        ]
                        if entity.id in related_ids:
                            score = entity.semantic_centrality
                            if score > best_score:
                                best_score = score
                                best_parent = node

                suggestions.append({
                    "entity_name": entity.name,
                    "entity_id": entity.id,
                    "suggested_parent": best_parent.name if best_parent else "Root",
                    "relevance_score": best_score,
                })

        return sorted(suggestions, key=lambda x: x["relevance_score"], reverse=True)[:10]

    def calculate_coverage_metrics(self) -> dict[str, Any]:
        """Calculate taxonomy coverage metrics."""
        total_entities = len(self.ontology.entities)
        categorized = set()
        for node in self.nodes.values():
            categorized.update(node.entity_ids)

        categorized_count = len(categorized)

        # Calculate depth distribution
        depth_counts = {}
        for node in self.nodes.values():
            depth_counts[node.level] = depth_counts.get(node.level, 0) + 1

        # Calculate link density
        total_links = sum(len(n.internal_links_to) for n in self.nodes.values())
        avg_links = total_links / len(self.nodes) if self.nodes else 0

        return {
            "total_nodes": len(self.nodes),
            "total_entities": total_entities,
            "entities_categorized": categorized_count,
            "coverage_percentage": (categorized_count / total_entities * 100) if total_entities else 0,
            "depth_distribution": depth_counts,
            "total_internal_links": total_links,
            "avg_links_per_node": round(avg_links, 2),
            "facet_count": len(self.facets),
            "total_facet_values": sum(len(v) for v in self.facets.values()),
        }
