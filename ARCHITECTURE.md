# AI Search Visibility Optimization - Architecture

## System Overview

```
USER INPUT
    ↓
┌─────────────────────────────────────┐
│  Brand Foundation Config            │
│  - brand_name                       │
│  - primary_niche                    │
│  - business_goals                   │
│  - source_mode (sitemap/seed)       │
│  - sitemap_url OR seed_entities     │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  STEP 1: ONTOLOGY BUILDER           │
│  Extract/Define entities & map      │
│  semantic relationships             │
│  Output: Ontology                   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  STEP 2: ENTITY SEARCH & EXPANSION  │
│  Identify target entities per goals │
│  Expand with synonyms/variants      │
│  Output: Expanded Ontology          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  STEP 3: TAXONOMY BUILDER           │
│  Create hierarchies & facets        │
│  Map internal linking structure     │
│  Output: Taxonomy                   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  STEP 4: QUERY MAPPING              │
│  Map entities to search queries     │
│  Plan query fan-out & rewrites      │
│  Output: QueryClusters              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  STEP 5: TOPICAL HUB DESIGN         │
│  Plan pillar + cluster structure    │
│  Internal link graph                │
│  Output: ContentHubs                │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  STEP 6: CONTENT SPECS              │
│  Recommend formats, schema, tone    │
│  Persona/SERP feature alignment     │
│  Output: ContentSpecs, Personas     │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  STEP 7: MEASUREMENT FRAMEWORK      │
│  Track AI Share of Voice setup      │
│  Define refresh cadence             │
│  Output: MeasurementPlan            │
└─────────────────────────────────────┘
    ↓
OUTPUT: FrameworkOutput (JSON/CSV/Markdown)
```

## Module Structure

```
ai-visibility-optimization-app/
├── app.py                          # Streamlit UI entry point
├── config/
│   ├── __init__.py
│   └── templates.py                # Configuration templates
│       ├── BrandFoundationConfig   # Main input configuration
│       ├── DEFAULT_RELATIONSHIP_TYPES
│       ├── DEFAULT_INTENT_TYPES
│       ├── DEFAULT_CONTENT_FORMATS
│       ├── DEFAULT_SCHEMA_TYPES
│       ├── QUERY_FANOUT_PATTERNS
│       ├── DEFAULT_PERSONA_TEMPLATES
│       └── DEFAULT_MEASUREMENT_KPIS
│
├── core/                           # Framework implementation
│   ├── __init__.py
│   ├── ontology_builder.py         # Step 1
│   │   └── OntologyBuilder
│   │       ├── build() -> Ontology
│   │       ├── _extract_from_sitemap()
│   │       ├── _create_from_seeds()
│   │       ├── _infer_relationships()
│   │       └── get_entity_graph_data()
│   │
│   ├── entity_search.py            # Step 2
│   │   └── EntitySearchExpander
│   │       ├── expand_all_entities() -> Ontology
│   │       ├── generate_semantic_variants()
│   │       ├── prioritize_entities()
│   │       └── find_entity_gaps()
│   │
│   ├── taxonomy_builder.py         # Step 3
│   │   └── TaxonomyBuilder
│   │       ├── build() -> Taxonomy
│   │       ├── _create_category_nodes()
│   │       ├── _generate_facets()
│   │       ├── _map_internal_links()
│   │       └── get_taxonomy_tree()
│   │
│   ├── query_mapper.py             # Step 4
│   │   └── QueryMapper
│   │       ├── map_all_entities() -> list[QueryCluster]
│   │       ├── _generate_fanout_queries()
│   │       ├── get_intent_coverage()
│   │       └── get_serp_feature_opportunities()
│   │
│   ├── hub_designer.py             # Step 5
│   │   └── HubDesigner
│   │       ├── design_all_hubs() -> list[ContentHub]
│   │       ├── _create_pillar_page()
│   │       ├── _create_cluster_pages()
│   │       └── suggest_content_gaps()
│   │
│   ├── content_specs.py            # Step 6
│   │   └── ContentSpecGenerator
│   │       ├── generate_all_specs() -> (Personas, Specs)
│   │       ├── _generate_content_structure()
│   │       ├── _generate_schema_markup()
│   │       └── _generate_ai_optimization_notes()
│   │
│   └── measurement_setup.py        # Step 7
│       └── MeasurementSetup
│           ├── create_measurement_plan() -> MeasurementPlan
│           ├── _create_kpis()
│           ├── _create_monitoring_queries()
│           └── get_ai_audit_prompts()
│
└── utils/
    ├── __init__.py
    ├── data_models.py              # Pydantic models
    │   ├── Entity, Relationship, Ontology
    │   ├── TaxonomyNode, Taxonomy
    │   ├── Query, QueryCluster
    │   ├── HubPage, ContentHub
    │   ├── Persona, ContentSpec
    │   ├── KPI, MeasurementPlan
    │   └── FrameworkOutput
    │
    ├── sitemap_parser.py           # XML sitemap parsing
    │   └── SitemapParser
    │       ├── parse_sitemap() -> SitemapAnalysis
    │       └── extract_entities_from_sitemap()
    │
    ├── exporters.py                # Export utilities
    │   └── Exporter
    │       ├── to_json()
    │       ├── to_markdown()
    │       ├── entities_to_csv()
    │       ├── queries_to_csv()
    │       └── content_hubs_to_csv()
    │
    └── validators.py               # Input validation
        └── InputValidator
            ├── validate_config()
            ├── validate_sitemap_url()
            └── validate_seed_entities()
```

## Data Flow

### 1. Input Configuration

```python
BrandFoundationConfig:
  - brand_name: str
  - primary_niche: str
  - business_goals: list[BusinessGoalType]
  - source_mode: SourceMode (seed/sitemap/hybrid)
  - sitemap_url: str | None
  - seed_entities: list[str]
  - competitors: list[str]
  - target_regions: list[str]
```

### 2. Processing Pipeline

```
Config → OntologyBuilder.build()
           ↓
       Ontology
           ↓
     EntitySearchExpander.expand_all_entities()
           ↓
   Expanded Ontology
           ↓
     TaxonomyBuilder.build()
           ↓
       Taxonomy
           ↓
     QueryMapper.map_all_entities()
           ↓
    QueryClusters[]
           ↓
     HubDesigner.design_all_hubs()
           ↓
     ContentHubs[]
           ↓
     ContentSpecGenerator.generate_all_specs()
           ↓
   (Personas[], ContentSpecs[])
           ↓
     MeasurementSetup.create_measurement_plan()
           ↓
    MeasurementPlan
           ↓
     FrameworkOutput
```

### 3. Output Model

```python
FrameworkOutput:
  - brand_name: str
  - primary_niche: str
  - generated_at: datetime
  - ontology: Ontology
  - taxonomy: Taxonomy
  - query_clusters: list[QueryCluster]
  - content_hubs: list[ContentHub]
  - personas: list[Persona]
  - content_specs: list[ContentSpec]
  - measurement_plan: MeasurementPlan
  - summary: dict
```

## Key Design Decisions

### 1. Modular Pipeline Architecture
Each step is an independent module that can be:
- Tested in isolation
- Extended without affecting other steps
- Run incrementally if needed

### 2. Pydantic Data Models
All data structures use Pydantic for:
- Type validation
- JSON serialization
- Clear contracts between modules

### 3. Configuration-Driven Defaults
Templates in `config/templates.py` provide:
- Relationship types
- Intent classifications
- Content format specs
- Schema type definitions
- Query fanout patterns
- Persona templates
- KPI definitions

### 4. Export Flexibility
Multiple export formats:
- JSON: Complete programmatic output
- Markdown: Human-readable documentation
- CSV: Spreadsheet-compatible for content planning

### 5. Streamlit Cloud Compatible
- Minimal dependencies
- No persistent storage required
- Session state for multi-step workflow
- All processing happens client-side

## Streamlit Cloud Deployment

### Requirements
- Python 3.10+
- Dependencies in `requirements.txt`
- No external databases
- No API keys required

### Free Tier Considerations
- All processing is CPU-bound
- No GPU requirements
- Session-based (no user persistence)
- Exports download directly to user

### Configuration
`.streamlit/config.toml` configures:
- Theme colors
- Upload limits
- Security settings

## Extension Points

### Adding New Entity Sources
Implement in `core/ontology_builder.py`:
```python
def _extract_from_api(self):
    # Custom API extraction logic
    pass
```

### Adding New Query Patterns
Add to `config/templates.py`:
```python
QUERY_FANOUT_PATTERNS["new_pattern"] = {
    "patterns": [...],
    "intent": "...",
    "priority": 2,
}
```

### Adding New Export Formats
Implement in `utils/exporters.py`:
```python
@staticmethod
def to_custom_format(output: FrameworkOutput) -> str:
    # Custom export logic
    pass
```

### Adding New KPIs
Add to `config/templates.py`:
```python
DEFAULT_MEASUREMENT_KPIS["new_kpi"] = {
    "description": "...",
    "measurement_method": "...",
    "refresh_cadence": "...",
    "priority": "...",
}
```
