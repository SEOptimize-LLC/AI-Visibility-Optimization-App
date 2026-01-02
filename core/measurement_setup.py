"""
Step 7: Measurement Framework Setup

Configures KPIs, tracking setup, content audit framework,
and refresh cadence for ongoing AI visibility monitoring.
"""

from datetime import datetime
from typing import Any

from config.templates import DEFAULT_MEASUREMENT_KPIS
from utils.data_models import (
    Ontology,
    QueryCluster,
    ContentHub,
    ContentSpec,
    MeasurementPlan,
    KPI,
    ContentAuditItem,
    ContentPriority,
)


class MeasurementSetup:
    """
    Set up measurement framework for AI visibility tracking.

    Creates:
    - KPI definitions and targets
    - AI monitoring query list
    - Content audit framework
    - Refresh schedules
    """

    # Content refresh cadence by type
    REFRESH_CADENCES = {
        "pillar": "quarterly",
        "cluster": "semi-annually",
        "supporting": "annually",
        "time_sensitive": "monthly",
        "evergreen": "annually",
    }

    def __init__(
        self,
        ontology: Ontology,
        query_clusters: list[QueryCluster],
        content_hubs: list[ContentHub],
        content_specs: list[ContentSpec],
        brand_name: str,
        competitors: list[str] | None = None,
    ):
        self.ontology = ontology
        self.query_clusters = query_clusters
        self.content_hubs = content_hubs
        self.content_specs = content_specs
        self.brand_name = brand_name
        self.competitors = competitors or []

    def create_measurement_plan(self) -> MeasurementPlan:
        """
        Create comprehensive measurement plan.

        Returns:
            MeasurementPlan with KPIs, monitoring queries, and schedules
        """
        plan = MeasurementPlan(brand_name=self.brand_name)

        # Create KPIs
        plan.kpis = self._create_kpis()

        # Create AI monitoring queries
        plan.ai_monitoring_queries = self._create_monitoring_queries()

        # Create content audit items
        plan.content_audit = self._create_content_audit()

        # Set refresh schedules
        plan.refresh_schedule = self._create_refresh_schedule()

        # Add competitor tracking
        plan.competitor_tracking = self.competitors

        return plan

    def _create_kpis(self) -> list[KPI]:
        """Create KPI definitions with targets."""
        kpis = []

        for kpi_key, kpi_config in DEFAULT_MEASUREMENT_KPIS.items():
            kpi_id = f"kpi_{kpi_key}"

            kpis.append(KPI(
                id=kpi_id,
                name=kpi_key.replace("_", " ").title(),
                description=kpi_config["description"],
                measurement_method=kpi_config["measurement_method"],
                refresh_cadence=kpi_config["refresh_cadence"],
                priority=kpi_config["priority"],
                baseline_value=None,  # To be set after initial measurement
                target_value=None,  # To be set based on baseline
            ))

        # Add custom KPIs based on content structure
        kpis.append(KPI(
            id="kpi_hub_coverage",
            name="Content Hub Coverage",
            description="Percentage of planned content hubs with complete pillar + cluster structure",
            measurement_method="Track content creation progress against hub plans",
            refresh_cadence="weekly",
            priority="high",
            target_value=100.0,  # Goal: complete all hubs
        ))

        kpis.append(KPI(
            id="kpi_query_coverage",
            name="Query Coverage Rate",
            description="Percentage of mapped queries with dedicated content",
            measurement_method="Cross-reference query clusters with published content",
            refresh_cadence="monthly",
            priority="high",
            target_value=80.0,  # Goal: cover 80% of mapped queries
        ))

        return kpis

    def _create_monitoring_queries(self) -> list[str]:
        """Create list of queries to monitor in AI systems."""
        queries = []

        # Brand-specific queries
        brand_lower = self.brand_name.lower()
        queries.extend([
            f"what is {brand_lower}",
            f"{brand_lower} review",
            f"is {brand_lower} good",
            f"{brand_lower} alternatives",
            f"{brand_lower} vs",
        ])

        # Entity-based queries (top entities)
        top_entities = sorted(
            self.ontology.entities,
            key=lambda e: e.semantic_centrality,
            reverse=True,
        )[:10]

        for entity in top_entities:
            entity_lower = entity.name.lower()
            queries.extend([
                f"what is {entity_lower}",
                f"best {entity_lower}",
                f"how to {entity_lower}",
            ])

        # High-priority queries from clusters
        for cluster in self.query_clusters:
            for query in cluster.queries:
                if query.priority in [ContentPriority.CRITICAL, ContentPriority.HIGH]:
                    if query.query_text not in queries:
                        queries.append(query.query_text)

        # Dedupe and limit
        seen = set()
        unique_queries = []
        for q in queries:
            q_lower = q.lower()
            if q_lower not in seen:
                seen.add(q_lower)
                unique_queries.append(q)

        return unique_queries[:50]

    def _create_content_audit(self) -> list[ContentAuditItem]:
        """Create content audit items for tracking freshness."""
        audit_items = []

        for spec in self.content_specs:
            # Determine update priority based on content priority and format
            update_priority = spec.priority

            # Time-sensitive formats need more frequent updates
            time_sensitive_formats = ["comparison_table", "product_review", "listicle"]
            if spec.recommended_format in time_sensitive_formats:
                if update_priority == ContentPriority.MEDIUM:
                    update_priority = ContentPriority.HIGH

            audit_items.append(ContentAuditItem(
                page_id=spec.page_id,
                url=spec.target_url or "",
                title=spec.title,
                last_updated=None,  # Will be populated when content exists
                freshness_score=0.0,  # Will be calculated based on last_updated
                update_priority=update_priority,
                recommended_updates=self._get_recommended_updates(spec),
            ))

        return audit_items

    def _get_recommended_updates(self, spec: ContentSpec) -> list[str]:
        """Get recommended update actions for a content spec."""
        updates = []

        # Base updates for all content
        updates.append("Review and update statistics/data points")
        updates.append("Verify all external links are working")
        updates.append("Update 'Last Modified' date in schema")

        # Format-specific updates
        format_updates = {
            "comparison_table": [
                "Update pricing information",
                "Check for new competitors/alternatives",
                "Refresh feature comparisons",
            ],
            "how_to_tutorial": [
                "Verify steps still work with latest versions",
                "Update screenshots if UI changed",
                "Add new tips based on user feedback",
            ],
            "product_review": [
                "Update product version information",
                "Refresh pros/cons based on changes",
                "Update rating if warranted",
            ],
            "long_form_guide": [
                "Add new sections for emerging topics",
                "Update examples with recent cases",
                "Refresh internal links to new content",
            ],
        }

        if spec.recommended_format in format_updates:
            updates.extend(format_updates[spec.recommended_format])

        return updates

    def _create_refresh_schedule(self) -> dict[str, str]:
        """Create content refresh schedule by content type."""
        schedule = {}

        # Page type schedules
        schedule["pillar_pages"] = self.REFRESH_CADENCES["pillar"]
        schedule["cluster_pages"] = self.REFRESH_CADENCES["cluster"]
        schedule["supporting_pages"] = self.REFRESH_CADENCES["supporting"]

        # Format-specific schedules
        schedule["comparison_content"] = "quarterly"
        schedule["how_to_tutorials"] = "semi-annually"
        schedule["product_reviews"] = "quarterly"
        schedule["glossary_definitions"] = "annually"
        schedule["case_studies"] = "annually"

        # Schema/technical refresh
        schedule["schema_markup_audit"] = "quarterly"
        schedule["internal_link_audit"] = "monthly"
        schedule["broken_link_check"] = "weekly"

        return schedule

    def get_priority_monitoring_list(self) -> list[dict[str, Any]]:
        """Get prioritized list of queries to monitor in AI systems."""
        monitoring_list = []

        # Group by topic/entity
        for cluster in self.query_clusters:
            high_priority_queries = [
                q for q in cluster.queries
                if q.priority in [ContentPriority.CRITICAL, ContentPriority.HIGH]
            ]

            if high_priority_queries:
                monitoring_list.append({
                    "entity": cluster.primary_entity_name,
                    "queries": [q.query_text for q in high_priority_queries[:5]],
                    "intent_distribution": cluster.intent_distribution,
                    "monitoring_priority": (
                        "critical" if any(q.priority == ContentPriority.CRITICAL for q in high_priority_queries)
                        else "high"
                    ),
                })

        return sorted(
            monitoring_list,
            key=lambda x: x["monitoring_priority"] == "critical",
            reverse=True,
        )

    def get_ai_audit_prompts(self) -> list[dict[str, str]]:
        """
        Generate prompts for auditing AI system responses.

        These prompts help check how AI describes your brand.
        """
        prompts = [
            {
                "category": "Brand Perception",
                "prompt": f"What is {self.brand_name}?",
                "check_for": "Accurate description, correct positioning, key differentiators",
            },
            {
                "category": "Brand Authority",
                "prompt": f"Is {self.brand_name} a good choice for [primary use case]?",
                "check_for": "Positive sentiment, accurate feature description, fair comparison",
            },
            {
                "category": "Competitive Position",
                "prompt": f"What are the alternatives to {self.brand_name}?",
                "check_for": "Fair comparison, accurate strengths/weaknesses, market position",
            },
            {
                "category": "Feature Accuracy",
                "prompt": f"What can you do with {self.brand_name}?",
                "check_for": "Accurate feature list, correct capabilities, no outdated info",
            },
            {
                "category": "Pricing Accuracy",
                "prompt": f"How much does {self.brand_name} cost?",
                "check_for": "Current pricing, correct tiers, accurate value proposition",
            },
        ]

        # Add entity-specific prompts
        top_entities = sorted(
            [e for e in self.ontology.entities if e.type.value == "core"],
            key=lambda e: e.semantic_centrality,
            reverse=True,
        )[:5]

        for entity in top_entities:
            prompts.append({
                "category": "Topical Authority",
                "prompt": f"What should I know about {entity.name}?",
                "check_for": f"Brand mention, accurate {entity.name} information, helpful context",
            })

        return prompts

    def get_competitor_tracking_setup(self) -> list[dict[str, Any]]:
        """Set up competitor tracking configuration."""
        tracking = []

        for competitor in self.competitors:
            tracking.append({
                "competitor": competitor,
                "monitor_queries": [
                    f"what is {competitor.lower()}",
                    f"{competitor.lower()} vs {self.brand_name.lower()}",
                    f"{competitor.lower()} review",
                    f"{competitor.lower()} alternatives",
                ],
                "track_metrics": [
                    "AI mention frequency",
                    "Sentiment in AI responses",
                    "Feature comparisons accuracy",
                    "Share of voice by topic",
                ],
            })

        return tracking

    def generate_measurement_report(self) -> dict[str, Any]:
        """Generate comprehensive measurement framework report."""
        plan = self.create_measurement_plan()

        return {
            "brand_name": self.brand_name,
            "total_kpis": len(plan.kpis),
            "monitoring_queries": len(plan.ai_monitoring_queries),
            "content_audit_items": len(plan.content_audit),
            "competitors_tracked": len(self.competitors),
            "kpi_summary": [
                {
                    "name": kpi.name,
                    "priority": kpi.priority,
                    "cadence": kpi.refresh_cadence,
                }
                for kpi in plan.kpis
            ],
            "refresh_schedule": plan.refresh_schedule,
            "priority_monitoring": self.get_priority_monitoring_list()[:10],
            "ai_audit_prompts": self.get_ai_audit_prompts(),
            "next_actions": [
                "Set up SERP monitoring for AI Overview detection",
                "Configure ChatGPT/Perplexity monitoring for brand mentions",
                "Establish baseline measurements for all KPIs",
                "Create content calendar aligned with refresh schedules",
                "Set up competitor tracking dashboards",
            ],
        }

    def get_quick_wins(self) -> list[dict[str, Any]]:
        """Identify quick wins for immediate impact."""
        quick_wins = []

        # High-priority content without coverage
        critical_specs = [
            s for s in self.content_specs
            if s.priority == ContentPriority.CRITICAL
        ]

        if critical_specs:
            quick_wins.append({
                "action": "Create critical priority content",
                "items": [s.title for s in critical_specs[:5]],
                "impact": "High - addresses most important visibility gaps",
                "effort": "Medium-High",
            })

        # Schema markup opportunities
        quick_wins.append({
            "action": "Implement structured data on existing pages",
            "items": ["FAQPage schema", "HowTo schema", "Article schema with author"],
            "impact": "Medium - improves AI extractability",
            "effort": "Low",
        })

        # Content freshness updates
        quick_wins.append({
            "action": "Update date-sensitive content",
            "items": ["Comparison pages", "Pricing pages", "Product reviews"],
            "impact": "Medium - signals recency to AI systems",
            "effort": "Low-Medium",
        })

        # Internal linking
        quick_wins.append({
            "action": "Strengthen internal linking",
            "items": ["Link new content to pillars", "Add contextual links between clusters"],
            "impact": "Medium - improves topical authority signals",
            "effort": "Low",
        })

        return quick_wins
