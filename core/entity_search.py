"""
Step 2: Entity Search & Expansion

Expands identified entities with synonyms, variants, and related terms
to increase semantic surface area.
"""

import re
from typing import Any

from utils.data_models import Entity, EntityType, Ontology


class EntitySearchExpander:
    """
    Expand entities with synonyms, variants, and related terms.

    This increases the "semantic surface area" for AI understanding
    by ensuring comprehensive coverage of how users might refer to concepts.
    """

    # Common suffix/prefix patterns for expansion
    SUFFIX_PATTERNS = {
        "tool": ["tools", "software", "platform", "app", "application"],
        "service": ["services", "solution", "solutions"],
        "guide": ["guides", "tutorial", "tutorials", "how-to"],
        "tips": ["tips", "advice", "best practices", "strategies"],
        "review": ["reviews", "comparison", "vs", "alternatives"],
    }

    # Intent modifiers that create query variants
    INTENT_MODIFIERS = {
        "informational": [
            "what is", "how to", "why", "guide to", "introduction to",
            "basics of", "understanding", "explained", "overview",
        ],
        "commercial": [
            "best", "top", "vs", "comparison", "alternatives to",
            "review", "pricing", "cost of", "free",
        ],
        "transactional": [
            "buy", "get", "download", "sign up for", "try",
            "demo", "free trial", "discount",
        ],
    }

    # Common abbreviation expansions
    ABBREVIATIONS = {
        "seo": "search engine optimization",
        "sem": "search engine marketing",
        "ppc": "pay per click",
        "cro": "conversion rate optimization",
        "ux": "user experience",
        "ui": "user interface",
        "api": "application programming interface",
        "ai": "artificial intelligence",
        "ml": "machine learning",
        "saas": "software as a service",
        "b2b": "business to business",
        "b2c": "business to consumer",
        "roi": "return on investment",
        "kpi": "key performance indicator",
        "cms": "content management system",
        "crm": "customer relationship management",
    }

    def __init__(self, ontology: Ontology):
        self.ontology = ontology

    def expand_all_entities(self) -> Ontology:
        """
        Expand all entities in the ontology with variants.

        Returns:
            Updated ontology with expanded entities
        """
        for entity in self.ontology.entities:
            self._expand_entity(entity)

        return self.ontology

    def _expand_entity(self, entity: Entity):
        """Expand a single entity with aliases and variants."""
        name_lower = entity.name.lower()

        # Start with existing aliases
        new_aliases = set(entity.aliases)

        # Add abbreviation expansions
        new_aliases.update(self._expand_abbreviations(name_lower))

        # Add plural/singular variants
        new_aliases.update(self._generate_number_variants(entity.name))

        # Add hyphen/space variants
        new_aliases.update(self._generate_format_variants(entity.name))

        # Add common suffix variants
        new_aliases.update(self._generate_suffix_variants(name_lower))

        # Add industry-specific variants
        new_aliases.update(self._generate_industry_variants(name_lower))

        # Filter and deduplicate
        new_aliases = {
            alias for alias in new_aliases
            if alias and alias.lower() != name_lower and len(alias) >= 2
        }

        entity.aliases = list(new_aliases)

    def _expand_abbreviations(self, name: str) -> set[str]:
        """Expand known abbreviations in entity name."""
        expansions = set()
        name_lower = name.lower()

        # Check if entire name is an abbreviation
        if name_lower in self.ABBREVIATIONS:
            expansions.add(self.ABBREVIATIONS[name_lower])

        # Check for abbreviations within the name
        words = name_lower.split()
        for i, word in enumerate(words):
            if word in self.ABBREVIATIONS:
                expanded_words = words.copy()
                expanded_words[i] = self.ABBREVIATIONS[word]
                expansions.add(" ".join(expanded_words))

        # Reverse: check if name matches an expansion
        for abbr, expansion in self.ABBREVIATIONS.items():
            if expansion.lower() in name_lower:
                expansions.add(name_lower.replace(expansion.lower(), abbr))

        return expansions

    def _generate_number_variants(self, name: str) -> set[str]:
        """Generate singular/plural variants."""
        variants = set()
        name_lower = name.lower()

        # Pluralization rules
        if name_lower.endswith("s") and not name_lower.endswith("ss"):
            # Potentially plural - add singular
            variants.add(name_lower[:-1])
            if name_lower.endswith("ies"):
                variants.add(name_lower[:-3] + "y")
            elif name_lower.endswith("es"):
                variants.add(name_lower[:-2])
        else:
            # Singular - add plural
            if name_lower.endswith("y") and len(name_lower) > 2:
                if name_lower[-2] not in "aeiou":
                    variants.add(name_lower[:-1] + "ies")
                else:
                    variants.add(name_lower + "s")
            elif name_lower.endswith(("s", "x", "z", "ch", "sh")):
                variants.add(name_lower + "es")
            else:
                variants.add(name_lower + "s")

        return variants

    def _generate_format_variants(self, name: str) -> set[str]:
        """Generate hyphen/space/camelCase variants."""
        variants = set()

        # Hyphen to space and vice versa
        if "-" in name:
            variants.add(name.replace("-", " "))
            variants.add(name.replace("-", ""))  # Concatenated
        elif " " in name:
            variants.add(name.replace(" ", "-"))
            variants.add(name.replace(" ", ""))  # Concatenated

        # CamelCase detection and splitting
        if not " " in name and not "-" in name:
            # Split camelCase
            split = re.sub("([A-Z])", r" \1", name).strip().lower()
            if split != name.lower():
                variants.add(split)
                variants.add(split.replace(" ", "-"))

        return variants

    def _generate_suffix_variants(self, name: str) -> set[str]:
        """Generate variants with common suffixes."""
        variants = set()

        for base_suffix, related_suffixes in self.SUFFIX_PATTERNS.items():
            if name.endswith(base_suffix):
                base = name[:-len(base_suffix)]
                for suffix in related_suffixes:
                    if suffix != base_suffix:
                        variants.add(base + suffix)

        return variants

    def _generate_industry_variants(self, name: str) -> set[str]:
        """Generate industry-specific variants."""
        variants = set()

        # Add common industry prefixes
        industry_prefixes = ["digital", "online", "cloud", "modern", "advanced"]
        for prefix in industry_prefixes:
            if name.startswith(prefix + " "):
                # Remove prefix
                variants.add(name[len(prefix) + 1:])
            elif not any(name.startswith(p + " ") for p in industry_prefixes):
                # Could add prefix, but be conservative
                pass

        return variants

    def generate_semantic_variants(self, entity: Entity) -> list[str]:
        """
        Generate semantic variants for query coverage.

        Returns list of terms that should appear in content
        targeting this entity.
        """
        variants = [entity.name] + entity.aliases

        # Add intent-modified variants
        name_lower = entity.name.lower()
        for intent, modifiers in self.INTENT_MODIFIERS.items():
            for modifier in modifiers[:3]:  # Limit per intent
                if not modifier.endswith(" "):
                    variants.append(f"{modifier} {name_lower}")

        return list(dict.fromkeys(variants))  # Dedupe while preserving order

    def get_semantic_surface_area(self, entity: Entity) -> dict[str, Any]:
        """
        Calculate semantic surface area coverage for an entity.

        Returns metrics about coverage breadth.
        """
        variants = self.generate_semantic_variants(entity)

        return {
            "entity_name": entity.name,
            "alias_count": len(entity.aliases),
            "total_variants": len(variants),
            "variants": variants[:20],  # Sample
            "coverage_score": min(1.0, len(variants) / 20),
            "intent_coverage": {
                intent: any(
                    any(mod in v.lower() for mod in mods)
                    for v in variants
                )
                for intent, mods in self.INTENT_MODIFIERS.items()
            },
        }

    def prioritize_entities(self) -> list[Entity]:
        """
        Prioritize entities by semantic centrality and commercial value.

        Returns sorted list of entities for content prioritization.
        """
        # Calculate composite score
        def score(entity: Entity) -> float:
            return (
                entity.semantic_centrality * 0.4 +
                entity.commercial_value * 0.4 +
                min(1.0, len(entity.aliases) / 10) * 0.2
            )

        # Sort by score descending
        return sorted(
            self.ontology.entities,
            key=score,
            reverse=True,
        )

    def find_entity_gaps(
        self,
        competitor_entities: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Identify entity gaps compared to competitors.

        Args:
            competitor_entities: List of entity names competitors cover

        Returns:
            List of gap analysis results
        """
        gaps = []
        our_entities = {e.name.lower() for e in self.ontology.entities}
        our_aliases = set()
        for entity in self.ontology.entities:
            our_aliases.update(a.lower() for a in entity.aliases)

        our_coverage = our_entities | our_aliases

        if competitor_entities:
            for comp_entity in competitor_entities:
                comp_lower = comp_entity.lower()
                if comp_lower not in our_coverage:
                    gaps.append({
                        "entity": comp_entity,
                        "gap_type": "missing",
                        "recommendation": f"Consider creating content covering '{comp_entity}'",
                        "priority": "high" if len(comp_entity.split()) <= 3 else "medium",
                    })

        return gaps

    def get_entity_cluster(self, entity_id: str) -> list[Entity]:
        """
        Get cluster of related entities.

        Returns entities connected by relationships.
        """
        cluster = []
        entity = self.ontology.get_entity(entity_id)

        if not entity:
            return cluster

        cluster.append(entity)

        # Get related entities
        for related_entity, _ in self.ontology.get_related_entities(entity_id):
            if related_entity not in cluster:
                cluster.append(related_entity)

        return cluster

    def generate_expansion_report(self) -> dict[str, Any]:
        """Generate report on entity expansion results."""
        total_aliases = sum(len(e.aliases) for e in self.ontology.entities)
        entities_with_aliases = sum(1 for e in self.ontology.entities if e.aliases)

        by_type = {}
        for entity in self.ontology.entities:
            type_key = entity.type.value
            if type_key not in by_type:
                by_type[type_key] = {"count": 0, "aliases": 0}
            by_type[type_key]["count"] += 1
            by_type[type_key]["aliases"] += len(entity.aliases)

        return {
            "total_entities": len(self.ontology.entities),
            "entities_with_aliases": entities_with_aliases,
            "total_aliases": total_aliases,
            "avg_aliases_per_entity": total_aliases / len(self.ontology.entities) if self.ontology.entities else 0,
            "by_type": by_type,
            "top_expanded": [
                {"name": e.name, "aliases": len(e.aliases)}
                for e in sorted(
                    self.ontology.entities,
                    key=lambda x: len(x.aliases),
                    reverse=True,
                )[:10]
            ],
        }
