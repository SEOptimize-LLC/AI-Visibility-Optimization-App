# AI Search Visibility Optimization App

A Streamlit application implementing the **7-Step AI Search Visibility Framework** for increasing brand visibility in AI-generated responses, AI Overviews, and LLM outputs.

Based on the framework from [iloveseo.net](https://www.iloveseo.net/what-framework-to-use-for-increasing-visibility-in-ai-search/)

## Features

- **Brand Ontology Builder**: Map semantic relationships between your brand entities
- **Entity Expansion**: Generate synonyms, variants, and semantic coverage
- **Taxonomy Optimization**: Create hierarchical structures with cross-cutting facets
- **Query Mapping**: Map entities to search queries with intent coverage
- **Content Hub Design**: Plan pillar + cluster content architecture
- **Content Specifications**: Generate detailed specs with schema markup recommendations
- **Measurement Framework**: Set up KPIs and AI monitoring strategies

## Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/your-org/AI-Visibility-Optimization-App.git
cd AI-Visibility-Optimization-App

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Deploy to Streamlit Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Select `app.py` as the main file
5. Deploy!

## Project Structure

```
ai-visibility-optimization-app/
├── app.py                      # Streamlit application entry point
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── config/
│   ├── __init__.py
│   └── templates.py           # Configuration templates & defaults
├── core/
│   ├── __init__.py
│   ├── ontology_builder.py    # Step 1: Build brand ontology
│   ├── entity_search.py       # Step 2: Entity expansion
│   ├── taxonomy_builder.py    # Step 3: Taxonomy optimization
│   ├── query_mapper.py        # Step 4: Query mapping
│   ├── hub_designer.py        # Step 5: Content hub design
│   ├── content_specs.py       # Step 6: Content specifications
│   └── measurement_setup.py   # Step 7: Measurement framework
├── utils/
│   ├── __init__.py
│   ├── data_models.py         # Pydantic data models
│   ├── sitemap_parser.py      # XML sitemap parsing
│   ├── exporters.py           # JSON/CSV/Markdown export
│   └── validators.py          # Input validation
└── README.md
```

## Framework Overview

### Step 1: Brand Ontology Design
- Extract entities from sitemap or seed list
- Map semantic relationships (is-a, part-of, used-for, relates-to)
- Calculate entity centrality and commercial value

### Step 2: Entity Identification & Expansion
- Generate synonyms and aliases
- Expand abbreviations
- Create semantic variants for coverage

### Step 3: Taxonomy Optimization
- Build hierarchical category structure
- Define cross-cutting facets
- Map internal linking structure

### Step 4: Query Mapping & Fan-out
- Generate queries using fan-out patterns
- Cover all search intents
- Map SERP feature opportunities

### Step 5: Topical Content Hubs
- Design pillar + cluster architecture
- Plan internal linking graphs
- Calculate coverage scores

### Step 6: Content Specifications
- Generate detailed content specs
- Recommend schema markup
- Provide AI optimization guidelines

### Step 7: Measurement Framework
- Define KPIs for AI visibility
- Create monitoring query lists
- Set content refresh schedules

## Export Formats

- **JSON**: Complete structured data for programmatic use
- **Markdown**: Human-readable summary document
- **CSV**: Spreadsheet-friendly data for content calendars

## Configuration

### Brand Foundation Config

```python
BrandFoundationConfig(
    brand_name="Your Brand",
    primary_niche="Your Industry",
    business_goals=[BusinessGoalType.BRAND_AWARENESS],
    source_mode=SourceMode.SEED,
    seed_entities=["entity1", "entity2"],
    competitors=["Competitor A", "Competitor B"],
)
```

### Source Modes

- **SEED**: Manually provide core entities
- **SITEMAP**: Auto-extract from XML sitemap
- **HYBRID**: Combine both approaches

## Requirements

- Python 3.10+
- Streamlit 1.28+
- Pydantic 2.0+
- httpx 0.25+

## License

MIT License

## Credits

Framework based on the AI Search Optimization methodology from [iloveseo.net](https://www.iloveseo.net/what-framework-to-use-for-increasing-visibility-in-ai-search/)
