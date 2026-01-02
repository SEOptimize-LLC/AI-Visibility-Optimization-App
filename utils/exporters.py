"""Export utilities for framework outputs in various formats."""

import json
import csv
import io
from datetime import datetime
from typing import Any

from .data_models import (
    FrameworkOutput,
    Ontology,
    Taxonomy,
    QueryCluster,
    ContentHub,
    ContentSpec,
    MeasurementPlan,
)


class Exporter:
    """
    Export framework outputs to various formats.

    Supports:
    - JSON (full structured data)
    - CSV (tabular data for spreadsheets)
    - Markdown (human-readable documentation)
    """

    @staticmethod
    def to_json(output: FrameworkOutput, indent: int = 2) -> str:
        """Export complete framework output to JSON."""
        return output.model_dump_json(indent=indent)

    @staticmethod
    def to_dict(output: FrameworkOutput) -> dict[str, Any]:
        """Export framework output to dictionary."""
        return output.model_dump()

    # =========================================================================
    # CSV Exports
    # =========================================================================

    @staticmethod
    def entities_to_csv(ontology: Ontology) -> str:
        """Export entities to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Entity ID",
            "Name",
            "Type",
            "Description",
            "Aliases",
            "Commercial Value",
            "Semantic Centrality",
            "Source URLs",
        ])

        # Data
        for entity in ontology.entities:
            writer.writerow([
                entity.id,
                entity.name,
                entity.type.value,
                entity.description or "",
                "; ".join(entity.aliases),
                entity.commercial_value,
                entity.semantic_centrality,
                "; ".join(entity.source_urls[:3]),
            ])

        return output.getvalue()

    @staticmethod
    def relationships_to_csv(ontology: Ontology) -> str:
        """Export relationships to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Source Entity",
            "Relationship Type",
            "Target Entity",
            "Weight",
            "Bidirectional",
            "Context",
        ])

        # Get entity name lookup
        entity_names = {e.id: e.name for e in ontology.entities}

        # Data
        for rel in ontology.relationships:
            writer.writerow([
                entity_names.get(rel.source_id, rel.source_id),
                rel.relationship_type.value,
                entity_names.get(rel.target_id, rel.target_id),
                rel.weight,
                "Yes" if rel.bidirectional else "No",
                rel.context or "",
            ])

        return output.getvalue()

    @staticmethod
    def taxonomy_to_csv(taxonomy: Taxonomy) -> str:
        """Export taxonomy to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Node ID",
            "Name",
            "Parent ID",
            "Level",
            "Facets",
            "SEO Title",
            "Target URL",
            "Entity IDs",
        ])

        # Data
        for node in taxonomy.nodes:
            writer.writerow([
                node.id,
                node.name,
                node.parent_id or "",
                node.level,
                "; ".join(node.facets),
                node.seo_title or "",
                node.target_url or "",
                "; ".join(node.entity_ids),
            ])

        return output.getvalue()

    @staticmethod
    def queries_to_csv(query_clusters: list[QueryCluster]) -> str:
        """Export queries to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Cluster ID",
            "Primary Entity",
            "Query",
            "Intent",
            "Priority",
            "Est. Volume",
            "SERP Features",
            "Fanout Pattern",
        ])

        # Data
        for cluster in query_clusters:
            for query in cluster.queries:
                writer.writerow([
                    cluster.id,
                    cluster.primary_entity_name,
                    query.query_text,
                    query.intent.value,
                    query.priority.value,
                    query.estimated_volume or "",
                    "; ".join(query.serp_features),
                    query.fanout_pattern or "",
                ])

        return output.getvalue()

    @staticmethod
    def content_hubs_to_csv(hubs: list[ContentHub]) -> str:
        """Export content hubs to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Hub Name",
            "Page ID",
            "Page Title",
            "Page Type",
            "Status",
            "Priority",
            "Target Queries",
            "Recommended Format",
            "Word Count",
            "Schema Types",
            "Existing URL",
            "Links To",
        ])

        # Data
        for hub in hubs:
            for page in hub.all_pages():
                writer.writerow([
                    hub.name,
                    page.id,
                    page.title,
                    page.page_type,
                    page.status,
                    page.priority.value,
                    "; ".join(page.target_queries[:3]),
                    page.recommended_format or "",
                    page.recommended_word_count or "",
                    "; ".join(page.schema_types),
                    page.existing_url or "",
                    "; ".join(page.internal_links_to[:5]),
                ])

        return output.getvalue()

    @staticmethod
    def content_specs_to_csv(specs: list[ContentSpec]) -> str:
        """Export content specifications to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Page ID",
            "Title",
            "Primary Query",
            "Secondary Queries",
            "Target Personas",
            "Format",
            "Word Count",
            "Content Structure",
            "Schema Types",
            "SERP Targets",
            "Priority",
        ])

        # Data
        for spec in specs:
            schema_types = [s.get("@type", "") for s in spec.schema_markup]
            writer.writerow([
                spec.page_id,
                spec.title,
                spec.primary_query,
                "; ".join(spec.secondary_queries[:3]),
                "; ".join(spec.target_personas),
                spec.recommended_format,
                spec.word_count_target or "",
                " > ".join(spec.content_structure[:5]),
                "; ".join(schema_types),
                "; ".join(spec.serp_feature_targets),
                spec.priority.value,
            ])

        return output.getvalue()

    # =========================================================================
    # Markdown Exports
    # =========================================================================

    @staticmethod
    def to_markdown(output: FrameworkOutput) -> str:
        """Export complete framework output to Markdown."""
        lines = [
            f"# AI Search Visibility Roadmap: {output.brand_name}",
            "",
            f"**Generated:** {output.generated_at.strftime('%Y-%m-%d %H:%M')}",
            f"**Primary Niche:** {output.primary_niche}",
            f"**Framework Version:** {output.version}",
            "",
        ]

        # Summary
        output.generate_summary()
        lines.extend([
            "## Executive Summary",
            "",
            "| Metric | Value |",
            "|--------|-------|",
        ])
        for key, value in output.summary.items():
            display_key = key.replace("_", " ").title()
            lines.append(f"| {display_key} | {value} |")
        lines.append("")

        # Ontology
        if output.ontology:
            lines.extend(Exporter._ontology_to_markdown(output.ontology))

        # Taxonomy
        if output.taxonomy:
            lines.extend(Exporter._taxonomy_to_markdown(output.taxonomy))

        # Query Clusters
        if output.query_clusters:
            lines.extend(Exporter._queries_to_markdown(output.query_clusters))

        # Content Hubs
        if output.content_hubs:
            lines.extend(Exporter._hubs_to_markdown(output.content_hubs))

        # Content Specs (summarized)
        if output.content_specs:
            lines.extend(Exporter._specs_to_markdown(output.content_specs))

        # Measurement Plan
        if output.measurement_plan:
            lines.extend(Exporter._measurement_to_markdown(output.measurement_plan))

        return "\n".join(lines)

    @staticmethod
    def _ontology_to_markdown(ontology: Ontology) -> list[str]:
        """Convert ontology to markdown section."""
        lines = [
            "## Step 1: Brand Ontology",
            "",
            "### Core Entities",
            "",
        ]

        # Group by type
        core_entities = [e for e in ontology.entities if e.type.value == "core"]
        supporting = [e for e in ontology.entities if e.type.value == "supporting"]

        for entity in core_entities[:20]:
            aliases_str = f" (aliases: {', '.join(entity.aliases)})" if entity.aliases else ""
            lines.append(f"- **{entity.name}**{aliases_str}")
            if entity.description:
                lines.append(f"  - {entity.description}")

        if supporting:
            lines.extend(["", "### Supporting Entities", ""])
            for entity in supporting[:15]:
                lines.append(f"- {entity.name}")

        # Key relationships
        lines.extend(["", "### Key Relationships", ""])
        entity_names = {e.id: e.name for e in ontology.entities}
        for rel in ontology.relationships[:20]:
            source = entity_names.get(rel.source_id, rel.source_id)
            target = entity_names.get(rel.target_id, rel.target_id)
            lines.append(f"- {source} → *{rel.relationship_type.value}* → {target}")

        lines.append("")
        return lines

    @staticmethod
    def _taxonomy_to_markdown(taxonomy: Taxonomy) -> list[str]:
        """Convert taxonomy to markdown section."""
        lines = [
            "## Step 3: Taxonomy Structure",
            "",
        ]

        # Build tree view
        root_nodes = taxonomy.get_root_nodes()
        for root in root_nodes:
            lines.append(f"### {root.name}")
            children = taxonomy.get_children(root.id)
            for child in children:
                lines.append(f"- {child.name}")
                grandchildren = taxonomy.get_children(child.id)
                for gc in grandchildren[:5]:
                    lines.append(f"  - {gc.name}")
            lines.append("")

        # Facets
        if taxonomy.facet_definitions:
            lines.extend(["### Cross-Cutting Facets", ""])
            for facet, values in taxonomy.facet_definitions.items():
                lines.append(f"- **{facet}:** {', '.join(values[:10])}")
            lines.append("")

        return lines

    @staticmethod
    def _queries_to_markdown(clusters: list[QueryCluster]) -> list[str]:
        """Convert query clusters to markdown section."""
        lines = [
            "## Step 4: Query Mapping",
            "",
            f"**Total Query Clusters:** {len(clusters)}",
            f"**Total Queries Mapped:** {sum(len(c.queries) for c in clusters)}",
            "",
        ]

        for cluster in clusters[:10]:
            lines.extend([
                f"### {cluster.primary_entity_name}",
                "",
            ])

            # Group by intent
            by_intent: dict[str, list[str]] = {}
            for query in cluster.queries:
                intent = query.intent.value
                if intent not in by_intent:
                    by_intent[intent] = []
                by_intent[intent].append(query.query_text)

            for intent, queries in by_intent.items():
                lines.append(f"**{intent.title()} Intent:**")
                for q in queries[:5]:
                    lines.append(f"- {q}")
                lines.append("")

        return lines

    @staticmethod
    def _hubs_to_markdown(hubs: list[ContentHub]) -> list[str]:
        """Convert content hubs to markdown section."""
        lines = [
            "## Step 5: Content Hub Architecture",
            "",
        ]

        for hub in hubs:
            lines.extend([
                f"### Hub: {hub.name}",
                "",
            ])

            if hub.pillar_page:
                status_icon = "✅" if hub.pillar_page.status == "exists" else "📝"
                lines.append(f"**Pillar Page:** {status_icon} {hub.pillar_page.title}")
                lines.append("")

            if hub.cluster_pages:
                lines.append("**Cluster Pages:**")
                for page in hub.cluster_pages:
                    status_icon = "✅" if page.status == "exists" else "📝"
                    lines.append(f"- {status_icon} {page.title} ({page.priority.value} priority)")
                lines.append("")

            lines.append(f"**Internal Links:** {hub.internal_link_count}")
            lines.append(f"**Coverage Score:** {hub.coverage_score:.0%}")
            lines.append("")

        return lines

    @staticmethod
    def _specs_to_markdown(specs: list[ContentSpec]) -> list[str]:
        """Convert content specs to markdown section."""
        lines = [
            "## Step 6: Content Specifications",
            "",
            f"**Total Specs Generated:** {len(specs)}",
            "",
        ]

        # Group by priority
        critical = [s for s in specs if s.priority.value == "critical"]
        high = [s for s in specs if s.priority.value == "high"]

        if critical:
            lines.append("### Critical Priority Content")
            lines.append("")
            for spec in critical[:10]:
                lines.append(f"#### {spec.title}")
                lines.append(f"- **Primary Query:** {spec.primary_query}")
                lines.append(f"- **Format:** {spec.recommended_format}")
                if spec.word_count_target:
                    lines.append(f"- **Target Length:** {spec.word_count_target} words")
                if spec.content_structure:
                    lines.append(f"- **Structure:** {' → '.join(spec.content_structure[:4])}")
                lines.append("")

        if high:
            lines.append("### High Priority Content")
            lines.append("")
            for spec in high[:10]:
                lines.append(f"- **{spec.title}** ({spec.recommended_format})")
            lines.append("")

        return lines

    @staticmethod
    def _measurement_to_markdown(plan: MeasurementPlan) -> list[str]:
        """Convert measurement plan to markdown section."""
        lines = [
            "## Step 7: Measurement Framework",
            "",
            "### Key Performance Indicators",
            "",
            "| KPI | Priority | Cadence | Measurement Method |",
            "|-----|----------|---------|-------------------|",
        ]

        for kpi in plan.kpis:
            lines.append(
                f"| {kpi.name} | {kpi.priority} | {kpi.refresh_cadence} | {kpi.measurement_method[:50]}... |"
            )

        lines.extend(["", "### AI Monitoring Queries", ""])
        for query in plan.ai_monitoring_queries[:10]:
            lines.append(f"- {query}")

        if plan.refresh_schedule:
            lines.extend(["", "### Content Refresh Schedule", ""])
            for content_type, cadence in plan.refresh_schedule.items():
                lines.append(f"- **{content_type}:** {cadence}")

        lines.append("")
        return lines

    # =========================================================================
    # File Writing Helpers
    # =========================================================================

    @staticmethod
    def get_all_exports(output: FrameworkOutput) -> dict[str, str]:
        """
        Generate all export formats at once.

        Returns dict with filename -> content.
        """
        exports = {
            "roadmap_complete.json": Exporter.to_json(output),
            "roadmap_summary.md": Exporter.to_markdown(output),
        }

        if output.ontology:
            exports["entities.csv"] = Exporter.entities_to_csv(output.ontology)
            exports["relationships.csv"] = Exporter.relationships_to_csv(output.ontology)

        if output.taxonomy:
            exports["taxonomy.csv"] = Exporter.taxonomy_to_csv(output.taxonomy)

        if output.query_clusters:
            exports["queries.csv"] = Exporter.queries_to_csv(output.query_clusters)

        if output.content_hubs:
            exports["content_hubs.csv"] = Exporter.content_hubs_to_csv(output.content_hubs)

        if output.content_specs:
            exports["content_specs.csv"] = Exporter.content_specs_to_csv(output.content_specs)

        return exports
