"""Input configuration templates for the AI Search Visibility Framework."""

from dataclasses import dataclass, field
from typing import Literal
from enum import Enum


class SourceMode(str, Enum):
    """How entities are sourced for analysis."""
    SITEMAP = "sitemap"
    SEED = "seed"
    HYBRID = "hybrid"


class BusinessGoalType(str, Enum):
    """Types of business goals for strategic alignment."""
    BRAND_AWARENESS = "brand_awareness"
    LEAD_GENERATION = "lead_generation"
    ECOMMERCE_SALES = "ecommerce_sales"
    THOUGHT_LEADERSHIP = "thought_leadership"
    LOCAL_VISIBILITY = "local_visibility"
    PRODUCT_ADOPTION = "product_adoption"


@dataclass
class BrandFoundationConfig:
    """
    Core configuration for brand analysis.

    This is the primary input that drives the entire framework.
    """
    brand_name: str
    primary_niche: str
    business_goals: list[BusinessGoalType]
    source_mode: SourceMode = SourceMode.SEED
    sitemap_url: str | None = None
    seed_entities: list[str] = field(default_factory=list)
    competitors: list[str] = field(default_factory=list)
    target_regions: list[str] = field(default_factory=lambda: ["US"])
    target_languages: list[str] = field(default_factory=lambda: ["en"])

    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        if not self.brand_name.strip():
            errors.append("Brand name is required")
        if not self.primary_niche.strip():
            errors.append("Primary niche is required")
        if not self.business_goals:
            errors.append("At least one business goal is required")
        if self.source_mode == SourceMode.SITEMAP and not self.sitemap_url:
            errors.append("Sitemap URL required when source_mode is 'sitemap'")
        if self.source_mode == SourceMode.SEED and not self.seed_entities:
            errors.append("Seed entities required when source_mode is 'seed'")
        return errors


# Default relationship types for ontology mapping
DEFAULT_RELATIONSHIP_TYPES = {
    "is_a": {
        "description": "Hierarchical classification (e.g., 'Python is_a programming language')",
        "weight": 1.0,
        "bidirectional": False,
    },
    "part_of": {
        "description": "Component relationship (e.g., 'authentication is part_of user management')",
        "weight": 0.9,
        "bidirectional": False,
    },
    "used_for": {
        "description": "Purpose relationship (e.g., 'React is used_for frontend development')",
        "weight": 0.8,
        "bidirectional": False,
    },
    "relates_to": {
        "description": "General semantic association (e.g., 'SEO relates_to content marketing')",
        "weight": 0.6,
        "bidirectional": True,
    },
    "requires": {
        "description": "Dependency relationship (e.g., 'deployment requires testing')",
        "weight": 0.7,
        "bidirectional": False,
    },
    "alternative_to": {
        "description": "Substitution relationship (e.g., 'Vue is alternative_to React')",
        "weight": 0.5,
        "bidirectional": True,
    },
    "enables": {
        "description": "Capability relationship (e.g., 'API enables integration')",
        "weight": 0.8,
        "bidirectional": False,
    },
    "contrasts_with": {
        "description": "Opposing concepts (e.g., 'agile contrasts_with waterfall')",
        "weight": 0.4,
        "bidirectional": True,
    },
}

# Default intent types for query mapping
DEFAULT_INTENT_TYPES = {
    "informational": {
        "description": "User seeks knowledge or understanding",
        "query_patterns": ["what is", "how to", "why", "guide", "tutorial", "explained"],
        "content_depth": "comprehensive",
    },
    "navigational": {
        "description": "User seeks specific page or resource",
        "query_patterns": ["login", "official", "website", "download", "pricing"],
        "content_depth": "direct",
    },
    "commercial": {
        "description": "User researching before purchase decision",
        "query_patterns": ["best", "vs", "comparison", "review", "top", "alternatives"],
        "content_depth": "comparative",
    },
    "transactional": {
        "description": "User ready to take action or purchase",
        "query_patterns": ["buy", "discount", "coupon", "free trial", "sign up", "demo"],
        "content_depth": "action-oriented",
    },
    "local": {
        "description": "User seeks location-specific results",
        "query_patterns": ["near me", "in [city]", "local", "nearby"],
        "content_depth": "location-aware",
    },
}

# Default content formats with AI-readiness scores
DEFAULT_CONTENT_FORMATS = {
    "long_form_guide": {
        "description": "Comprehensive pillar content (2000+ words)",
        "ai_extractability": 0.9,
        "serp_features": ["featured_snippet", "paa"],
        "schema_types": ["Article", "HowTo"],
        "best_for_intents": ["informational"],
    },
    "comparison_table": {
        "description": "Structured comparison content",
        "ai_extractability": 0.95,
        "serp_features": ["table_snippet", "featured_snippet"],
        "schema_types": ["Table", "ItemList"],
        "best_for_intents": ["commercial"],
    },
    "how_to_tutorial": {
        "description": "Step-by-step instructional content",
        "ai_extractability": 0.9,
        "serp_features": ["how_to_rich_result", "featured_snippet"],
        "schema_types": ["HowTo"],
        "best_for_intents": ["informational"],
    },
    "faq_page": {
        "description": "Question and answer format",
        "ai_extractability": 0.85,
        "serp_features": ["faq_rich_result", "paa"],
        "schema_types": ["FAQPage"],
        "best_for_intents": ["informational", "navigational"],
    },
    "product_review": {
        "description": "In-depth product analysis",
        "ai_extractability": 0.8,
        "serp_features": ["review_snippet", "star_rating"],
        "schema_types": ["Review", "Product"],
        "best_for_intents": ["commercial", "transactional"],
    },
    "listicle": {
        "description": "Numbered/bulleted list content",
        "ai_extractability": 0.85,
        "serp_features": ["featured_snippet", "list_snippet"],
        "schema_types": ["ItemList", "Article"],
        "best_for_intents": ["informational", "commercial"],
    },
    "video_content": {
        "description": "Video with transcript and chapters",
        "ai_extractability": 0.7,
        "serp_features": ["video_carousel", "key_moments"],
        "schema_types": ["VideoObject"],
        "best_for_intents": ["informational"],
    },
    "tool_calculator": {
        "description": "Interactive tool or calculator",
        "ai_extractability": 0.5,
        "serp_features": ["web_app"],
        "schema_types": ["WebApplication", "SoftwareApplication"],
        "best_for_intents": ["transactional"],
    },
    "case_study": {
        "description": "Real-world example with results",
        "ai_extractability": 0.75,
        "serp_features": ["featured_snippet"],
        "schema_types": ["Article", "Report"],
        "best_for_intents": ["commercial"],
    },
    "glossary_definition": {
        "description": "Term definitions and explanations",
        "ai_extractability": 0.95,
        "serp_features": ["definition_snippet", "knowledge_panel"],
        "schema_types": ["DefinedTerm", "Article"],
        "best_for_intents": ["informational"],
    },
}

# Default schema types for structured data
DEFAULT_SCHEMA_TYPES = {
    "Article": {
        "required_fields": ["headline", "author", "datePublished", "image"],
        "recommended_fields": ["dateModified", "publisher", "description"],
        "ai_value": "High - enables article understanding and citation",
    },
    "HowTo": {
        "required_fields": ["name", "step"],
        "recommended_fields": ["totalTime", "estimatedCost", "supply", "tool", "image"],
        "ai_value": "Very High - directly extractable for AI responses",
    },
    "FAQPage": {
        "required_fields": ["mainEntity"],
        "recommended_fields": [],
        "ai_value": "Very High - Q&A format ideal for AI extraction",
    },
    "Product": {
        "required_fields": ["name", "image", "description"],
        "recommended_fields": ["offers", "aggregateRating", "review", "brand", "sku"],
        "ai_value": "High - enables product recommendations",
    },
    "Review": {
        "required_fields": ["itemReviewed", "author"],
        "recommended_fields": ["reviewRating", "reviewBody", "datePublished"],
        "ai_value": "Medium-High - supports sentiment analysis",
    },
    "VideoObject": {
        "required_fields": ["name", "description", "thumbnailUrl", "uploadDate"],
        "recommended_fields": ["duration", "contentUrl", "embedUrl", "hasPart"],
        "ai_value": "Medium - video content less extractable but valuable",
    },
    "Organization": {
        "required_fields": ["name", "url"],
        "recommended_fields": ["logo", "sameAs", "contactPoint", "address"],
        "ai_value": "High - establishes entity identity",
    },
    "Person": {
        "required_fields": ["name"],
        "recommended_fields": ["jobTitle", "worksFor", "sameAs", "image"],
        "ai_value": "High - establishes author expertise (E-E-A-T)",
    },
    "BreadcrumbList": {
        "required_fields": ["itemListElement"],
        "recommended_fields": [],
        "ai_value": "Medium - helps AI understand site structure",
    },
    "ItemList": {
        "required_fields": ["itemListElement"],
        "recommended_fields": ["numberOfItems", "itemListOrder"],
        "ai_value": "High - structured lists are AI-friendly",
    },
    "DefinedTerm": {
        "required_fields": ["name", "description"],
        "recommended_fields": ["inDefinedTermSet"],
        "ai_value": "Very High - ideal for knowledge extraction",
    },
    "WebApplication": {
        "required_fields": ["name", "url"],
        "recommended_fields": ["applicationCategory", "operatingSystem", "offers"],
        "ai_value": "Medium - for interactive tools",
    },
}

# Query fan-out patterns for Step 4
QUERY_FANOUT_PATTERNS = {
    "definitional": {
        "patterns": ["what is {entity}", "{entity} meaning", "{entity} definition", "{entity} explained"],
        "intent": "informational",
        "priority": 1,
    },
    "how_to": {
        "patterns": ["how to {entity}", "{entity} tutorial", "{entity} guide", "learn {entity}"],
        "intent": "informational",
        "priority": 1,
    },
    "comparison": {
        "patterns": ["{entity} vs", "{entity} alternatives", "{entity} comparison", "best {entity}"],
        "intent": "commercial",
        "priority": 2,
    },
    "problems": {
        "patterns": ["{entity} problems", "{entity} issues", "{entity} not working", "{entity} errors"],
        "intent": "informational",
        "priority": 2,
    },
    "benefits": {
        "patterns": ["{entity} benefits", "why use {entity}", "{entity} advantages", "{entity} pros cons"],
        "intent": "commercial",
        "priority": 2,
    },
    "examples": {
        "patterns": ["{entity} examples", "{entity} use cases", "{entity} templates", "{entity} samples"],
        "intent": "informational",
        "priority": 2,
    },
    "pricing": {
        "patterns": ["{entity} pricing", "{entity} cost", "{entity} free", "is {entity} free"],
        "intent": "transactional",
        "priority": 3,
    },
    "reviews": {
        "patterns": ["{entity} review", "{entity} reviews", "is {entity} good", "{entity} worth it"],
        "intent": "commercial",
        "priority": 2,
    },
    "integration": {
        "patterns": ["{entity} integration", "{entity} with", "{entity} api", "{entity} plugins"],
        "intent": "informational",
        "priority": 3,
    },
    "advanced": {
        "patterns": ["advanced {entity}", "{entity} best practices", "{entity} tips", "{entity} optimization"],
        "intent": "informational",
        "priority": 3,
    },
}

# Persona templates for Step 6
DEFAULT_PERSONA_TEMPLATES = {
    "beginner": {
        "knowledge_level": "novice",
        "preferred_formats": ["how_to_tutorial", "faq_page", "video_content"],
        "content_tone": "educational, supportive, jargon-free",
        "key_motivations": ["learning fundamentals", "avoiding mistakes", "quick wins"],
        "pain_points": ["overwhelmed by options", "unclear where to start"],
    },
    "practitioner": {
        "knowledge_level": "intermediate",
        "preferred_formats": ["long_form_guide", "comparison_table", "case_study"],
        "content_tone": "practical, detailed, example-driven",
        "key_motivations": ["improving efficiency", "solving specific problems", "staying current"],
        "pain_points": ["time constraints", "finding reliable information"],
    },
    "expert": {
        "knowledge_level": "advanced",
        "preferred_formats": ["case_study", "tool_calculator", "long_form_guide"],
        "content_tone": "technical, nuanced, data-driven",
        "key_motivations": ["optimization", "innovation", "thought leadership"],
        "pain_points": ["generic content", "outdated information"],
    },
    "decision_maker": {
        "knowledge_level": "varies",
        "preferred_formats": ["comparison_table", "product_review", "case_study"],
        "content_tone": "ROI-focused, executive summary style",
        "key_motivations": ["risk mitigation", "cost justification", "competitive advantage"],
        "pain_points": ["information overload", "vendor bias"],
    },
}

# Measurement KPIs for Step 7
DEFAULT_MEASUREMENT_KPIS = {
    "ai_share_of_voice": {
        "description": "Frequency of brand citations in AI-generated answers",
        "measurement_method": "Track mentions across ChatGPT, Perplexity, AI Overviews",
        "refresh_cadence": "weekly",
        "priority": "critical",
    },
    "ai_overview_presence": {
        "description": "Appearance in Google AI Overviews for target queries",
        "measurement_method": "Automated SERP monitoring with AI Overview detection",
        "refresh_cadence": "daily",
        "priority": "critical",
    },
    "topical_authority_score": {
        "description": "Depth and breadth of entity cluster coverage",
        "measurement_method": "Internal scoring based on content coverage matrix",
        "refresh_cadence": "monthly",
        "priority": "high",
    },
    "branded_search_volume": {
        "description": "Search volume trends for brand-related queries",
        "measurement_method": "Google Search Console, SEMrush, Ahrefs",
        "refresh_cadence": "monthly",
        "priority": "high",
    },
    "entity_association_accuracy": {
        "description": "How accurately AI describes brand vs intended positioning",
        "measurement_method": "Prompt AI systems about brand, analyze responses",
        "refresh_cadence": "monthly",
        "priority": "medium",
    },
    "content_freshness_score": {
        "description": "Recency of content updates across key pages",
        "measurement_method": "Track last-modified dates, content audit",
        "refresh_cadence": "weekly",
        "priority": "medium",
    },
    "schema_coverage": {
        "description": "Percentage of pages with valid structured data",
        "measurement_method": "Schema validation crawl",
        "refresh_cadence": "weekly",
        "priority": "medium",
    },
    "internal_link_health": {
        "description": "Hub-spoke link structure integrity",
        "measurement_method": "Internal link audit, orphan page detection",
        "refresh_cadence": "monthly",
        "priority": "medium",
    },
}
