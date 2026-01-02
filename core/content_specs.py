"""
Step 6: Content Specification Generator

Generates detailed content specifications with format recommendations,
schema markup, persona alignment, and AI optimization notes.
"""

import hashlib
from typing import Any

from config.templates import (
    DEFAULT_CONTENT_FORMATS,
    DEFAULT_SCHEMA_TYPES,
    DEFAULT_PERSONA_TEMPLATES,
)
from utils.data_models import (
    Entity,
    Ontology,
    ContentHub,
    HubPage,
    ContentSpec,
    Persona,
    IntentType,
    ContentPriority,
)


class ContentSpecGenerator:
    """
    Generate detailed content specifications for planned pages.

    Creates specifications including:
    - Content structure recommendations
    - Schema markup requirements
    - Persona targeting
    - AI optimization guidelines
    - SERP feature targeting
    """

    def __init__(
        self,
        ontology: Ontology,
        content_hubs: list[ContentHub],
        brand_name: str,
    ):
        self.ontology = ontology
        self.content_hubs = content_hubs
        self.brand_name = brand_name
        self.personas: list[Persona] = []
        self.specs: list[ContentSpec] = []

    def generate_all_specs(self) -> tuple[list[Persona], list[ContentSpec]]:
        """
        Generate personas and content specs for all planned pages.

        Returns:
            Tuple of (personas, content_specs)
        """
        # First, create personas
        self._create_personas()

        # Generate specs for each hub's pages
        for hub in self.content_hubs:
            for page in hub.all_pages():
                spec = self._generate_page_spec(page, hub)
                self.specs.append(spec)

        return self.personas, self.specs

    def _create_personas(self):
        """Create target audience personas."""
        for persona_key, template in DEFAULT_PERSONA_TEMPLATES.items():
            persona_id = f"persona_{persona_key}"

            self.personas.append(Persona(
                id=persona_id,
                name=persona_key.replace("_", " ").title(),
                knowledge_level=template["knowledge_level"],
                preferred_formats=template["preferred_formats"],
                content_tone=template["content_tone"],
                motivations=template["key_motivations"],
                pain_points=template["pain_points"],
                query_modifiers=self._get_persona_query_modifiers(persona_key),
            ))

    def _get_persona_query_modifiers(self, persona_key: str) -> list[str]:
        """Get query modifiers typical for a persona."""
        modifiers = {
            "beginner": ["beginner", "basics", "introduction", "simple", "easy", "for dummies"],
            "practitioner": ["best practices", "tips", "advanced", "professional", "efficient"],
            "expert": ["enterprise", "scale", "optimization", "architecture", "deep dive"],
            "decision_maker": ["roi", "comparison", "enterprise", "pricing", "case study"],
        }
        return modifiers.get(persona_key, [])

    def _generate_page_spec(
        self,
        page: HubPage,
        hub: ContentHub,
    ) -> ContentSpec:
        """Generate detailed content specification for a page."""
        spec_id = f"spec_{page.id}"

        # Determine target personas based on page type and intents
        target_personas = self._match_personas(page)

        # Get primary query
        primary_query = page.target_queries[0] if page.target_queries else page.title.lower()

        # Generate content structure
        structure = self._generate_content_structure(page, hub)

        # Generate schema markup
        schema_markup = self._generate_schema_markup(page, hub)

        # Generate AI optimization notes
        ai_notes = self._generate_ai_optimization_notes(page)

        # Determine SERP feature targets
        serp_targets = self._determine_serp_targets(page)

        # Generate internal link anchors
        link_anchors = self._generate_link_anchors(page, hub)

        # Determine content tone
        tone = self._determine_content_tone(target_personas, page.target_intents)

        # Calculate estimated impact
        impact = self._estimate_impact(page, hub)

        return ContentSpec(
            page_id=page.id,
            title=page.title,
            target_url=self._generate_target_url(page, hub),
            primary_query=primary_query,
            secondary_queries=page.target_queries[1:5] if len(page.target_queries) > 1 else [],
            target_personas=target_personas,
            recommended_format=page.recommended_format or "long_form_guide",
            content_structure=structure,
            schema_markup=schema_markup,
            ai_optimization_notes=ai_notes,
            serp_feature_targets=serp_targets,
            internal_link_anchors=link_anchors,
            word_count_target=page.recommended_word_count,
            content_tone=tone,
            priority=page.priority,
            estimated_impact=impact,
        )

    def _match_personas(self, page: HubPage) -> list[str]:
        """Match page to relevant personas."""
        matched = []

        for persona in self.personas:
            # Check format match
            if page.recommended_format in persona.preferred_formats:
                matched.append(persona.id)
                continue

            # Check intent match
            intent_persona_map = {
                IntentType.INFORMATIONAL: ["beginner", "practitioner"],
                IntentType.COMMERCIAL: ["decision_maker", "practitioner"],
                IntentType.TRANSACTIONAL: ["decision_maker"],
            }

            for intent in page.target_intents:
                personas_for_intent = intent_persona_map.get(intent, [])
                if persona.name.lower().replace(" ", "_") in personas_for_intent:
                    if persona.id not in matched:
                        matched.append(persona.id)

        return matched if matched else [self.personas[0].id]  # Default to first persona

    def _generate_content_structure(
        self,
        page: HubPage,
        hub: ContentHub,
    ) -> list[str]:
        """Generate recommended content structure (H2/H3 sections)."""
        format_type = page.recommended_format or "long_form_guide"

        # Get entity for context
        entity = None
        if page.entity_ids:
            entity = self.ontology.get_entity(page.entity_ids[0])

        entity_name = entity.name if entity else hub.name

        # Structure templates by format
        structures = {
            "long_form_guide": [
                f"What is {entity_name}?",
                "Key Features & Benefits",
                "How It Works",
                "Getting Started Guide",
                "Best Practices",
                "Common Challenges & Solutions",
                "Advanced Tips",
                "Frequently Asked Questions",
                "Conclusion & Next Steps",
            ],
            "how_to_tutorial": [
                "Overview & Prerequisites",
                "Step 1: Initial Setup",
                "Step 2: Configuration",
                "Step 3: Implementation",
                "Step 4: Testing & Validation",
                "Troubleshooting Common Issues",
                "Next Steps",
            ],
            "comparison_table": [
                "Quick Comparison Overview",
                "Feature-by-Feature Comparison",
                "Pricing Comparison",
                "Pros & Cons Summary",
                "Use Case Recommendations",
                "Our Verdict",
            ],
            "faq_page": [
                f"Most Common {entity_name} Questions",
                "Getting Started FAQs",
                "Technical FAQs",
                "Pricing & Plans FAQs",
                "Troubleshooting FAQs",
            ],
            "product_review": [
                "Product Overview",
                "Key Features Tested",
                "Performance Analysis",
                "Pros & Cons",
                "Pricing & Value",
                "Alternatives to Consider",
                "Final Verdict",
            ],
            "listicle": [
                "Introduction",
                f"Top {entity_name} Options",
                "How We Evaluated",
                "Detailed Breakdown",
                "Recommendations by Use Case",
            ],
            "case_study": [
                "Executive Summary",
                "The Challenge",
                "The Solution",
                "Implementation Details",
                "Results & Metrics",
                "Key Takeaways",
            ],
            "glossary_definition": [
                "Definition",
                "Key Concepts",
                "How It Works",
                "Examples",
                "Related Terms",
            ],
        }

        return structures.get(format_type, structures["long_form_guide"])

    def _generate_schema_markup(
        self,
        page: HubPage,
        hub: ContentHub,
    ) -> list[dict[str, Any]]:
        """Generate schema markup specifications."""
        schemas = []

        for schema_type in page.schema_types:
            schema_config = DEFAULT_SCHEMA_TYPES.get(schema_type, {})

            schema = {
                "@type": schema_type,
                "required_fields": schema_config.get("required_fields", []),
                "recommended_fields": schema_config.get("recommended_fields", []),
                "implementation_notes": self._get_schema_notes(schema_type, page),
            }

            schemas.append(schema)

        # Always add Organization schema reference
        schemas.append({
            "@type": "Organization",
            "note": f"Reference {self.brand_name} organization entity",
            "required_fields": ["name", "url", "logo"],
        })

        return schemas

    def _get_schema_notes(self, schema_type: str, page: HubPage) -> str:
        """Get implementation notes for a schema type."""
        notes = {
            "Article": "Include author, datePublished, dateModified. Link to author Person schema.",
            "HowTo": "Break into clear steps with step[].name and step[].text. Include time estimates.",
            "FAQPage": "Each Q&A must be in mainEntity array with Question and acceptedAnswer.",
            "Product": "Include offers with price, availability. Add aggregateRating if reviews exist.",
            "Review": "Requires itemReviewed. Include reviewRating with ratingValue and bestRating.",
            "VideoObject": "Include duration, thumbnailUrl, uploadDate. Add hasPart for chapters.",
            "BreadcrumbList": "Reflect taxonomy hierarchy. Include position for each item.",
            "ItemList": "Use for lists/rankings. Include itemListElement with position.",
        }
        return notes.get(schema_type, "Implement according to schema.org specifications.")

    def _generate_ai_optimization_notes(self, page: HubPage) -> list[str]:
        """Generate AI-specific optimization recommendations."""
        notes = [
            "Lead each section with the core answer (inverted pyramid structure)",
            "Use clear, descriptive H2/H3 headings that can stand alone as context",
            "Include a TL;DR or key takeaways section at the top",
            "Chunk content into modular, self-contained sections",
            "Use bullet points and numbered lists for extractable content",
        ]

        # Format-specific notes
        format_notes = {
            "how_to_tutorial": [
                "Number each step clearly (Step 1, Step 2, etc.)",
                "Include estimated time for each step",
                "Add 'Prerequisites' section at the beginning",
            ],
            "comparison_table": [
                "Use actual HTML tables for comparisons",
                "Include clear verdict/recommendation",
                "Add 'Best for' categorizations",
            ],
            "faq_page": [
                "Answer questions in the first sentence",
                "Keep answers concise but complete",
                "Group related questions together",
            ],
            "long_form_guide": [
                "Include a table of contents with anchor links",
                "Add 'Quick Summary' section after introduction",
                "Use definition boxes for key terms",
            ],
        }

        if page.recommended_format in format_notes:
            notes.extend(format_notes[page.recommended_format])

        # Add E-E-A-T notes for credibility
        notes.extend([
            "Include author credentials and expertise signals",
            "Add 'Last Updated' date and commit to quarterly reviews",
            "Reference primary sources and link to authoritative external content",
            "Include first-hand experience, original insights, or unique data",
        ])

        return notes

    def _determine_serp_targets(self, page: HubPage) -> list[str]:
        """Determine which SERP features to target."""
        targets = []

        format_config = DEFAULT_CONTENT_FORMATS.get(
            page.recommended_format or "long_form_guide", {}
        )
        targets.extend(format_config.get("serp_features", []))

        # Add based on intent
        for intent in page.target_intents:
            if intent == IntentType.INFORMATIONAL:
                if "featured_snippet" not in targets:
                    targets.append("featured_snippet")
                if "paa" not in targets:
                    targets.append("paa")
            elif intent == IntentType.COMMERCIAL:
                if "paa" not in targets:
                    targets.append("paa")
            elif intent == IntentType.TRANSACTIONAL:
                targets.append("site_links")

        return list(dict.fromkeys(targets))  # Dedupe

    def _generate_link_anchors(
        self,
        page: HubPage,
        hub: ContentHub,
    ) -> dict[str, str]:
        """Generate recommended anchor text for internal links."""
        anchors = {}

        # Link to pillar
        if hub.pillar_page and page.id != hub.pillar_page.id:
            anchors[f"comprehensive {hub.name} guide"] = hub.pillar_page.id
            anchors[f"learn more about {hub.name}"] = hub.pillar_page.id

        # Links to clusters
        for cluster in hub.cluster_pages:
            if cluster.id != page.id and cluster.id in page.internal_links_to:
                # Generate contextual anchor
                title_words = cluster.title.lower().split()[:4]
                anchor = " ".join(title_words)
                anchors[anchor] = cluster.id

        return anchors

    def _determine_content_tone(
        self,
        persona_ids: list[str],
        intents: list[IntentType],
    ) -> str:
        """Determine appropriate content tone."""
        tones = []

        for persona_id in persona_ids:
            persona = next((p for p in self.personas if p.id == persona_id), None)
            if persona:
                tones.append(persona.content_tone)

        if not tones:
            # Default based on intent
            if IntentType.COMMERCIAL in intents or IntentType.TRANSACTIONAL in intents:
                return "professional, persuasive, benefit-focused"
            else:
                return "educational, clear, helpful"

        # Combine tones
        return tones[0]  # Use primary persona's tone

    def _generate_target_url(self, page: HubPage, hub: ContentHub) -> str:
        """Generate target URL for page."""
        import re

        # Create slug from title
        slug = page.title.lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"\s+", "-", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")

        # Add hub context for non-pillar pages
        if page.page_type == "pillar":
            return f"/{slug}/"
        else:
            hub_slug = re.sub(r"[^a-z0-9\s-]", "", hub.name.lower())
            hub_slug = re.sub(r"\s+", "-", hub_slug)
            return f"/{hub_slug}/{slug}/"

    def _estimate_impact(self, page: HubPage, hub: ContentHub) -> str:
        """Estimate potential visibility impact."""
        factors = []

        # Priority impact
        if page.priority == ContentPriority.CRITICAL:
            factors.append("high-priority topic")
        elif page.priority == ContentPriority.HIGH:
            factors.append("significant topic")

        # Page type impact
        if page.page_type == "pillar":
            factors.append("pillar page (hub anchor)")

        # Intent impact
        if IntentType.COMMERCIAL in page.target_intents:
            factors.append("commercial intent (conversion potential)")
        if IntentType.TRANSACTIONAL in page.target_intents:
            factors.append("transactional intent (high conversion)")

        # Query count impact
        if len(page.target_queries) >= 5:
            factors.append("multiple query targets")

        if not factors:
            return "Standard visibility impact expected"

        return f"High impact: {', '.join(factors)}"

    def get_spec_by_priority(self) -> dict[str, list[ContentSpec]]:
        """Group specs by priority."""
        grouped: dict[str, list[ContentSpec]] = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
        }

        for spec in self.specs:
            grouped[spec.priority.value].append(spec)

        return grouped

    def generate_content_calendar_data(self) -> list[dict[str, Any]]:
        """Generate data for content calendar planning."""
        calendar_items = []

        # Sort by priority
        priority_order = {
            ContentPriority.CRITICAL: 0,
            ContentPriority.HIGH: 1,
            ContentPriority.MEDIUM: 2,
            ContentPriority.LOW: 3,
        }

        sorted_specs = sorted(
            self.specs,
            key=lambda s: priority_order.get(s.priority, 4),
        )

        for i, spec in enumerate(sorted_specs):
            calendar_items.append({
                "order": i + 1,
                "title": spec.title,
                "format": spec.recommended_format,
                "word_count": spec.word_count_target,
                "priority": spec.priority.value,
                "primary_query": spec.primary_query,
                "target_url": spec.target_url,
                "estimated_impact": spec.estimated_impact,
            })

        return calendar_items

    def generate_spec_report(self) -> dict[str, Any]:
        """Generate comprehensive content specification report."""
        by_priority = self.get_spec_by_priority()
        by_format: dict[str, int] = {}
        total_word_count = 0

        for spec in self.specs:
            fmt = spec.recommended_format
            by_format[fmt] = by_format.get(fmt, 0) + 1
            if spec.word_count_target:
                total_word_count += spec.word_count_target

        return {
            "total_specs": len(self.specs),
            "total_personas": len(self.personas),
            "total_planned_words": total_word_count,
            "by_priority": {k: len(v) for k, v in by_priority.items()},
            "by_format": by_format,
            "personas": [
                {
                    "name": p.name,
                    "knowledge_level": p.knowledge_level,
                    "preferred_formats": p.preferred_formats,
                }
                for p in self.personas
            ],
            "critical_content": [
                {"title": s.title, "format": s.recommended_format, "impact": s.estimated_impact}
                for s in by_priority.get("critical", [])
            ],
        }
