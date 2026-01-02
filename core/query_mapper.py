"""
Step 4: Query Mapping & Fan-out

Maps entities to search queries, plans query fan-out patterns,
and anticipates query rewrites for comprehensive intent coverage.
"""

import hashlib
from typing import Any

from config.templates import QUERY_FANOUT_PATTERNS, DEFAULT_INTENT_TYPES
from utils.data_models import (
    Entity,
    Ontology,
    Query,
    QueryCluster,
    IntentType,
    ContentPriority,
)


class QueryMapper:
    """
    Map entities to search queries with fan-out coverage.

    Creates comprehensive query clusters that cover:
    - All search intents (informational, commercial, etc.)
    - Query rewrites and variations
    - Fan-out patterns (how-to, vs, problems, etc.)
    """

    def __init__(self, ontology: Ontology):
        self.ontology = ontology
        self.clusters: dict[str, QueryCluster] = {}

    def map_all_entities(self) -> list[QueryCluster]:
        """
        Create query clusters for all core entities.

        Returns:
            List of query clusters with mapped queries
        """
        # Process core entities first (highest priority)
        core_entities = [
            e for e in self.ontology.entities
            if e.type.value == "core"
        ]

        for entity in core_entities:
            cluster = self._create_query_cluster(entity)
            self.clusters[cluster.id] = cluster

        # Also process high-value supporting entities
        supporting = [
            e for e in self.ontology.entities
            if e.type.value == "supporting" and e.semantic_centrality > 0.5
        ]

        for entity in supporting:
            cluster = self._create_query_cluster(entity)
            self.clusters[cluster.id] = cluster

        return list(self.clusters.values())

    def _create_query_cluster(self, entity: Entity) -> QueryCluster:
        """Create a query cluster for an entity."""
        cluster_id = f"qc_{hashlib.md5(entity.id.encode()).hexdigest()[:8]}"

        cluster = QueryCluster(
            id=cluster_id,
            primary_entity_id=entity.id,
            primary_entity_name=entity.name,
        )

        # Generate queries from fan-out patterns
        queries = self._generate_fanout_queries(entity)

        # Generate queries from aliases
        for alias in entity.aliases[:5]:
            queries.extend(self._generate_alias_queries(alias, entity.id))

        # Add queries to cluster
        for query in queries:
            cluster.add_query(query)

        return cluster

    def _generate_fanout_queries(self, entity: Entity) -> list[Query]:
        """Generate queries using fan-out patterns."""
        queries = []
        entity_name = entity.name.lower()

        for pattern_name, pattern_config in QUERY_FANOUT_PATTERNS.items():
            patterns = pattern_config["patterns"]
            intent_str = pattern_config["intent"]
            priority_val = pattern_config["priority"]

            # Map priority number to enum
            priority_map = {1: ContentPriority.CRITICAL, 2: ContentPriority.HIGH, 3: ContentPriority.MEDIUM}
            priority = priority_map.get(priority_val, ContentPriority.MEDIUM)

            # Map intent string to enum
            intent = IntentType(intent_str)

            for pattern in patterns[:3]:  # Limit patterns per category
                query_text = pattern.replace("{entity}", entity_name)

                queries.append(Query(
                    query_text=query_text,
                    intent=intent,
                    entity_ids=[entity.id],
                    priority=priority,
                    serp_features=self._predict_serp_features(pattern_name, intent),
                    fanout_pattern=pattern_name,
                ))

        return queries

    def _generate_alias_queries(self, alias: str, entity_id: str) -> list[Query]:
        """Generate basic queries for entity aliases."""
        queries = []
        alias_lower = alias.lower()

        # Basic informational query
        queries.append(Query(
            query_text=f"what is {alias_lower}",
            intent=IntentType.INFORMATIONAL,
            entity_ids=[entity_id],
            priority=ContentPriority.MEDIUM,
            fanout_pattern="alias_definitional",
        ))

        # How-to query
        queries.append(Query(
            query_text=f"how to use {alias_lower}",
            intent=IntentType.INFORMATIONAL,
            entity_ids=[entity_id],
            priority=ContentPriority.MEDIUM,
            fanout_pattern="alias_howto",
        ))

        return queries

    def _predict_serp_features(
        self,
        pattern_name: str,
        intent: IntentType,
    ) -> list[str]:
        """Predict likely SERP features for a query pattern."""
        features = []

        # Pattern-based predictions
        pattern_features = {
            "definitional": ["featured_snippet", "knowledge_panel"],
            "how_to": ["featured_snippet", "how_to_rich_result", "video_carousel"],
            "comparison": ["featured_snippet", "table_snippet"],
            "problems": ["paa", "featured_snippet"],
            "benefits": ["featured_snippet", "paa"],
            "examples": ["featured_snippet", "image_pack"],
            "pricing": ["product_results", "shopping_ads"],
            "reviews": ["review_snippet", "star_rating"],
            "integration": ["paa", "featured_snippet"],
            "advanced": ["featured_snippet", "paa"],
        }

        if pattern_name in pattern_features:
            features.extend(pattern_features[pattern_name])

        # Intent-based additions
        if intent == IntentType.COMMERCIAL:
            if "shopping_ads" not in features:
                features.append("paa")
        elif intent == IntentType.TRANSACTIONAL:
            features.append("site_links")

        return list(dict.fromkeys(features))  # Dedupe

    def generate_query_variations(
        self,
        base_query: str,
        entity_id: str,
    ) -> list[Query]:
        """
        Generate variations of a base query.

        Handles query rewrites that AI systems might perform.
        """
        variations = []
        base_lower = base_query.lower()

        # Question variations
        question_starters = ["what is", "how to", "why", "when to", "where to"]
        for starter in question_starters:
            if not base_lower.startswith(starter):
                # Try adding the starter
                new_query = f"{starter} {base_lower}"
                if len(new_query) < 100:
                    variations.append(Query(
                        query_text=new_query,
                        intent=IntentType.INFORMATIONAL,
                        entity_ids=[entity_id],
                        priority=ContentPriority.LOW,
                        fanout_pattern="variation",
                    ))

        # Action variations
        action_words = ["use", "implement", "install", "configure", "set up"]
        for action in action_words:
            new_query = f"how to {action} {base_lower}"
            if len(new_query) < 100:
                variations.append(Query(
                    query_text=new_query,
                    intent=IntentType.INFORMATIONAL,
                    entity_ids=[entity_id],
                    priority=ContentPriority.LOW,
                    fanout_pattern="action_variation",
                ))

        return variations[:10]  # Limit variations

    def get_intent_coverage(self, cluster: QueryCluster) -> dict[str, Any]:
        """Analyze intent coverage for a query cluster."""
        coverage = {
            "total_queries": len(cluster.queries),
            "by_intent": cluster.intent_distribution,
            "missing_intents": [],
            "coverage_score": 0.0,
        }

        # Check which intents are covered
        all_intents = [it.value for it in IntentType]
        covered_intents = set(cluster.intent_distribution.keys())

        # Calculate coverage
        for intent in all_intents:
            if intent not in covered_intents:
                coverage["missing_intents"].append(intent)

        coverage["coverage_score"] = len(covered_intents) / len(all_intents)

        return coverage

    def prioritize_queries(self) -> list[Query]:
        """
        Get all queries prioritized for content creation.

        Returns flat list of queries sorted by priority.
        """
        all_queries = []
        for cluster in self.clusters.values():
            all_queries.extend(cluster.queries)

        # Sort by priority then by intent type (commercial > informational)
        priority_order = {
            ContentPriority.CRITICAL: 0,
            ContentPriority.HIGH: 1,
            ContentPriority.MEDIUM: 2,
            ContentPriority.LOW: 3,
        }

        intent_order = {
            IntentType.TRANSACTIONAL: 0,
            IntentType.COMMERCIAL: 1,
            IntentType.INFORMATIONAL: 2,
            IntentType.NAVIGATIONAL: 3,
            IntentType.LOCAL: 4,
        }

        return sorted(
            all_queries,
            key=lambda q: (
                priority_order.get(q.priority, 5),
                intent_order.get(q.intent, 5),
            ),
        )

    def get_serp_feature_opportunities(self) -> dict[str, list[Query]]:
        """
        Group queries by SERP feature opportunity.

        Returns dict mapping SERP features to relevant queries.
        """
        opportunities: dict[str, list[Query]] = {}

        for cluster in self.clusters.values():
            for query in cluster.queries:
                for feature in query.serp_features:
                    if feature not in opportunities:
                        opportunities[feature] = []
                    opportunities[feature].append(query)

        # Sort by opportunity count
        return dict(
            sorted(
                opportunities.items(),
                key=lambda x: len(x[1]),
                reverse=True,
            )
        )

    def generate_query_report(self) -> dict[str, Any]:
        """Generate comprehensive query mapping report."""
        total_queries = sum(len(c.queries) for c in self.clusters.values())

        # Intent distribution across all clusters
        intent_totals: dict[str, int] = {}
        for cluster in self.clusters.values():
            for intent, count in cluster.intent_distribution.items():
                intent_totals[intent] = intent_totals.get(intent, 0) + count

        # Pattern distribution
        pattern_totals: dict[str, int] = {}
        for cluster in self.clusters.values():
            for query in cluster.queries:
                if query.fanout_pattern:
                    pattern_totals[query.fanout_pattern] = (
                        pattern_totals.get(query.fanout_pattern, 0) + 1
                    )

        # Priority distribution
        priority_totals: dict[str, int] = {}
        for cluster in self.clusters.values():
            for query in cluster.queries:
                p = query.priority.value
                priority_totals[p] = priority_totals.get(p, 0) + 1

        # SERP feature opportunities
        serp_opportunities = self.get_serp_feature_opportunities()
        serp_summary = {k: len(v) for k, v in serp_opportunities.items()}

        return {
            "total_clusters": len(self.clusters),
            "total_queries": total_queries,
            "avg_queries_per_cluster": (
                total_queries / len(self.clusters) if self.clusters else 0
            ),
            "intent_distribution": intent_totals,
            "pattern_distribution": pattern_totals,
            "priority_distribution": priority_totals,
            "serp_opportunities": serp_summary,
            "top_volume_clusters": [
                {
                    "entity": c.primary_entity_name,
                    "query_count": len(c.queries),
                    "total_volume": c.total_estimated_volume,
                }
                for c in sorted(
                    self.clusters.values(),
                    key=lambda x: len(x.queries),
                    reverse=True,
                )[:10]
            ],
        }

    def suggest_query_gaps(self, target_intent: IntentType) -> list[dict[str, Any]]:
        """
        Suggest queries to fill intent gaps.

        Returns entities that lack queries for the target intent.
        """
        gaps = []

        for cluster in self.clusters.values():
            intent_key = target_intent.value
            if intent_key not in cluster.intent_distribution:
                gaps.append({
                    "entity_name": cluster.primary_entity_name,
                    "entity_id": cluster.primary_entity_id,
                    "missing_intent": target_intent.value,
                    "current_intents": list(cluster.intent_distribution.keys()),
                    "suggested_queries": self._suggest_intent_queries(
                        cluster.primary_entity_name,
                        target_intent,
                    ),
                })

        return gaps

    def _suggest_intent_queries(
        self,
        entity_name: str,
        intent: IntentType,
    ) -> list[str]:
        """Suggest queries for a specific intent."""
        entity_lower = entity_name.lower()

        suggestions = {
            IntentType.INFORMATIONAL: [
                f"what is {entity_lower}",
                f"how does {entity_lower} work",
                f"{entity_lower} explained",
            ],
            IntentType.COMMERCIAL: [
                f"best {entity_lower}",
                f"{entity_lower} alternatives",
                f"{entity_lower} vs",
            ],
            IntentType.TRANSACTIONAL: [
                f"buy {entity_lower}",
                f"{entity_lower} pricing",
                f"{entity_lower} free trial",
            ],
            IntentType.NAVIGATIONAL: [
                f"{entity_lower} login",
                f"{entity_lower} official site",
            ],
            IntentType.LOCAL: [
                f"{entity_lower} near me",
                f"local {entity_lower}",
            ],
        }

        return suggestions.get(intent, [])
