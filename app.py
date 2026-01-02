"""
AI Search Visibility Optimization Framework

A Streamlit application implementing the 7-step framework for
increasing visibility in AI Search, AI Overviews, and LLM responses.

Based on the framework from iloveseo.net
"""

import streamlit as st
from datetime import datetime

# Import framework components
from config.templates import (
    BrandFoundationConfig,
    SourceMode,
    BusinessGoalType,
)
from core.ontology_builder import OntologyBuilder
from core.entity_search import EntitySearchExpander
from core.taxonomy_builder import TaxonomyBuilder
from core.query_mapper import QueryMapper
from core.hub_designer import HubDesigner
from core.content_specs import ContentSpecGenerator
from core.measurement_setup import MeasurementSetup
from utils.data_models import FrameworkOutput
from utils.exporters import Exporter
from utils.validators import InputValidator

# Page configuration
st.set_page_config(
    page_title="AI Search Visibility Optimizer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .step-header {
        background: linear-gradient(90deg, #1f77b4, #2ca02c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #1f77b4, #2ca02c);
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "step" not in st.session_state:
        st.session_state.step = 0
    if "config" not in st.session_state:
        st.session_state.config = None
    if "output" not in st.session_state:
        st.session_state.output = None
    if "processing" not in st.session_state:
        st.session_state.processing = False


def render_sidebar():
    """Render the sidebar with navigation and info."""
    with st.sidebar:
        st.markdown("### Navigation")

        steps = [
            "Configuration",
            "1. Ontology",
            "2. Entities",
            "3. Taxonomy",
            "4. Queries",
            "5. Hubs",
            "6. Content",
            "7. Measurement",
            "Export",
        ]

        for i, step_name in enumerate(steps):
            if i <= st.session_state.step:
                if st.button(step_name, key=f"nav_{i}", use_container_width=True):
                    st.session_state.step = i
            else:
                st.button(
                    step_name,
                    key=f"nav_{i}",
                    use_container_width=True,
                    disabled=True,
                )

        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This tool implements the **7-Step AI Search Visibility Framework**
        for optimizing content to appear in AI-generated responses.

        [Learn more about the framework](https://www.iloveseo.net/what-framework-to-use-for-increasing-visibility-in-ai-search/)
        """)

        if st.session_state.output:
            st.markdown("---")
            st.markdown("### Quick Stats")
            summary = st.session_state.output.summary
            st.metric("Entities", summary.get("total_entities", 0))
            st.metric("Query Clusters", summary.get("query_clusters", 0))
            st.metric("Content Pages", summary.get("total_pages_planned", 0))


def render_configuration_step():
    """Render the initial configuration step."""
    st.markdown('<p class="main-header">AI Search Visibility Optimizer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Configure your brand foundation to generate a comprehensive AI visibility roadmap</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Brand Foundation")

        brand_name = st.text_input(
            "Brand Name *",
            placeholder="e.g., Acme Corp",
            help="Your company or product name",
        )

        primary_niche = st.text_input(
            "Primary Niche *",
            placeholder="e.g., Project Management Software",
            help="Your main industry or category",
        )

        business_goals = st.multiselect(
            "Business Goals *",
            options=[g.value for g in BusinessGoalType],
            format_func=lambda x: x.replace("_", " ").title(),
            help="Select one or more business objectives",
        )

    with col2:
        st.markdown("### Data Source")

        source_mode = st.radio(
            "Entity Source",
            options=["seed", "sitemap", "hybrid"],
            format_func=lambda x: {
                "seed": "Seed Entities (Manual)",
                "sitemap": "Sitemap (Auto-extract)",
                "hybrid": "Hybrid (Both)",
            }[x],
            help="How to identify your initial entities",
        )

        if source_mode in ["seed", "hybrid"]:
            seed_entities_text = st.text_area(
                "Seed Entities (one per line)",
                placeholder="project management\ntask tracking\nteam collaboration\nworkflow automation",
                height=120,
                help="Enter your core topics/entities",
            )
            seed_entities = [
                e.strip() for e in seed_entities_text.split("\n")
                if e.strip()
            ]
        else:
            seed_entities = []

        if source_mode in ["sitemap", "hybrid"]:
            sitemap_url = st.text_input(
                "Sitemap URL",
                placeholder="https://example.com/sitemap.xml",
                help="URL to your XML sitemap",
            )
        else:
            sitemap_url = None

    st.markdown("### Optional Settings")

    col3, col4 = st.columns(2)

    with col3:
        competitors_text = st.text_area(
            "Competitors (one per line)",
            placeholder="Competitor A\nCompetitor B",
            height=80,
            help="Optional: List your main competitors",
        )
        competitors = [
            c.strip() for c in competitors_text.split("\n")
            if c.strip()
        ]

    with col4:
        target_regions = st.multiselect(
            "Target Regions",
            options=["US", "UK", "EU", "APAC", "Global"],
            default=["US"],
            help="Primary target markets",
        )

    st.markdown("---")

    # Validation and submission
    if st.button("Generate AI Visibility Roadmap", type="primary", use_container_width=True):
        # Create config
        try:
            config = BrandFoundationConfig(
                brand_name=brand_name,
                primary_niche=primary_niche,
                business_goals=[BusinessGoalType(g) for g in business_goals],
                source_mode=SourceMode(source_mode),
                sitemap_url=sitemap_url,
                seed_entities=seed_entities,
                competitors=competitors,
                target_regions=target_regions,
            )

            # Validate
            errors = InputValidator.validate_config(config)
            if InputValidator.has_errors(errors):
                for error in errors:
                    if error.severity == "error":
                        st.error(f"{error.field}: {error.message}")
                return

            # Show warnings
            warnings = [e for e in errors if e.severity == "warning"]
            for warning in warnings:
                st.warning(f"{warning.field}: {warning.message}")

            # Store config and proceed
            st.session_state.config = config
            st.session_state.processing = True
            st.rerun()

        except Exception as e:
            st.error(f"Configuration error: {str(e)}")


def process_framework():
    """Process the complete framework pipeline."""
    config = st.session_state.config

    progress = st.progress(0, text="Starting framework processing...")

    try:
        # Step 1: Build Ontology
        progress.progress(10, text="Step 1: Building brand ontology...")
        ontology_builder = OntologyBuilder(config)
        ontology = ontology_builder.build()

        # Step 2: Expand Entities
        progress.progress(25, text="Step 2: Expanding entities...")
        entity_expander = EntitySearchExpander(ontology)
        ontology = entity_expander.expand_all_entities()

        # Step 3: Build Taxonomy
        progress.progress(40, text="Step 3: Building taxonomy...")
        taxonomy_builder = TaxonomyBuilder(ontology, config.primary_niche)
        taxonomy = taxonomy_builder.build()

        # Step 4: Map Queries
        progress.progress(55, text="Step 4: Mapping queries...")
        query_mapper = QueryMapper(ontology)
        query_clusters = query_mapper.map_all_entities()

        # Step 5: Design Hubs
        progress.progress(70, text="Step 5: Designing content hubs...")
        hub_designer = HubDesigner(ontology, taxonomy, query_clusters)
        content_hubs = hub_designer.design_all_hubs()

        # Step 6: Generate Content Specs
        progress.progress(85, text="Step 6: Generating content specifications...")
        spec_generator = ContentSpecGenerator(ontology, content_hubs, config.brand_name)
        personas, content_specs = spec_generator.generate_all_specs()

        # Step 7: Setup Measurement
        progress.progress(95, text="Step 7: Setting up measurement framework...")
        measurement_setup = MeasurementSetup(
            ontology=ontology,
            query_clusters=query_clusters,
            content_hubs=content_hubs,
            content_specs=content_specs,
            brand_name=config.brand_name,
            competitors=config.competitors,
        )
        measurement_plan = measurement_setup.create_measurement_plan()

        # Create output
        output = FrameworkOutput(
            brand_name=config.brand_name,
            primary_niche=config.primary_niche,
            ontology=ontology,
            taxonomy=taxonomy,
            query_clusters=query_clusters,
            content_hubs=content_hubs,
            personas=personas,
            content_specs=content_specs,
            measurement_plan=measurement_plan,
        )
        output.generate_summary()

        progress.progress(100, text="Complete!")

        st.session_state.output = output
        st.session_state.processing = False
        st.session_state.step = 1

        st.rerun()

    except Exception as e:
        progress.empty()
        st.error(f"Processing error: {str(e)}")
        st.session_state.processing = False


def render_step_1_ontology():
    """Render Step 1: Ontology visualization."""
    st.markdown('<p class="step-header">Step 1: Brand Ontology</p>', unsafe_allow_html=True)
    st.markdown("Your brand's semantic entity map and relationships")

    output = st.session_state.output
    ontology = output.ontology

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Entities", len(ontology.entities))
    with col2:
        st.metric("Relationships", len(ontology.relationships))
    with col3:
        counts = ontology.entity_count_by_type()
        st.metric("Core Entities", counts.get("core", 0))

    # Entity list
    st.markdown("### Entities")

    entity_df_data = []
    for entity in ontology.entities:
        entity_df_data.append({
            "Name": entity.name,
            "Type": entity.type.value,
            "Centrality": f"{entity.semantic_centrality:.2f}",
            "Commercial Value": f"{entity.commercial_value:.2f}",
            "Aliases": ", ".join(entity.aliases[:3]) + ("..." if len(entity.aliases) > 3 else ""),
        })

    st.dataframe(entity_df_data, use_container_width=True)

    # Relationships
    with st.expander("View Relationships"):
        entity_names = {e.id: e.name for e in ontology.entities}
        for rel in ontology.relationships[:20]:
            source = entity_names.get(rel.source_id, rel.source_id)
            target = entity_names.get(rel.target_id, rel.target_id)
            st.text(f"{source} → {rel.relationship_type.value} → {target}")

    if st.button("Next: Entity Expansion →", type="primary"):
        st.session_state.step = 2
        st.rerun()


def render_step_2_entities():
    """Render Step 2: Entity expansion details."""
    st.markdown('<p class="step-header">Step 2: Entity Expansion</p>', unsafe_allow_html=True)
    st.markdown("Expanded entities with synonyms and semantic variants")

    output = st.session_state.output
    ontology = output.ontology

    # Expansion stats
    total_aliases = sum(len(e.aliases) for e in ontology.entities)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Aliases Generated", total_aliases)
    with col2:
        avg = total_aliases / len(ontology.entities) if ontology.entities else 0
        st.metric("Avg Aliases per Entity", f"{avg:.1f}")

    # Top expanded entities
    st.markdown("### Top Expanded Entities")

    top_expanded = sorted(
        ontology.entities,
        key=lambda e: len(e.aliases),
        reverse=True,
    )[:10]

    for entity in top_expanded:
        with st.expander(f"{entity.name} ({len(entity.aliases)} aliases)"):
            st.write("**Aliases:**", ", ".join(entity.aliases))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Ontology"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("Next: Taxonomy →", type="primary"):
            st.session_state.step = 3
            st.rerun()


def render_step_3_taxonomy():
    """Render Step 3: Taxonomy structure."""
    st.markdown('<p class="step-header">Step 3: Taxonomy Structure</p>', unsafe_allow_html=True)
    st.markdown("Hierarchical category structure for navigation")

    output = st.session_state.output
    taxonomy = output.taxonomy

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Taxonomy Nodes", len(taxonomy.nodes))
    with col2:
        st.metric("Facets Defined", len(taxonomy.facet_definitions))
    with col3:
        total_links = sum(len(n.internal_links_to) for n in taxonomy.nodes)
        st.metric("Internal Links", total_links)

    # Tree view
    st.markdown("### Category Hierarchy")

    root_nodes = taxonomy.get_root_nodes()
    for root in root_nodes:
        st.markdown(f"**{root.name}**")
        children = taxonomy.get_children(root.id)
        for child in children:
            st.markdown(f"  └─ {child.name}")
            grandchildren = taxonomy.get_children(child.id)
            for gc in grandchildren[:3]:
                st.markdown(f"      └─ {gc.name}")

    # Facets
    if taxonomy.facet_definitions:
        st.markdown("### Cross-Cutting Facets")
        for facet, values in taxonomy.facet_definitions.items():
            st.markdown(f"**{facet}:** {', '.join(list(values)[:10])}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Entities"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("Next: Query Mapping →", type="primary"):
            st.session_state.step = 4
            st.rerun()


def render_step_4_queries():
    """Render Step 4: Query mapping."""
    st.markdown('<p class="step-header">Step 4: Query Mapping</p>', unsafe_allow_html=True)
    st.markdown("Search queries mapped to entities with intent coverage")

    output = st.session_state.output
    clusters = output.query_clusters

    total_queries = sum(len(c.queries) for c in clusters)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Query Clusters", len(clusters))
    with col2:
        st.metric("Total Queries", total_queries)
    with col3:
        avg = total_queries / len(clusters) if clusters else 0
        st.metric("Avg Queries/Cluster", f"{avg:.1f}")

    # Intent distribution
    st.markdown("### Intent Distribution")

    intent_totals = {}
    for cluster in clusters:
        for intent, count in cluster.intent_distribution.items():
            intent_totals[intent] = intent_totals.get(intent, 0) + count

    intent_df = [{"Intent": k, "Count": v} for k, v in intent_totals.items()]
    st.bar_chart(data={d["Intent"]: d["Count"] for d in intent_df})

    # Query clusters
    st.markdown("### Query Clusters")

    for cluster in clusters[:5]:
        with st.expander(f"{cluster.primary_entity_name} ({len(cluster.queries)} queries)"):
            for query in cluster.queries[:10]:
                st.text(f"[{query.intent.value}] {query.query_text}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Taxonomy"):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("Next: Content Hubs →", type="primary"):
            st.session_state.step = 5
            st.rerun()


def render_step_5_hubs():
    """Render Step 5: Content hub design."""
    st.markdown('<p class="step-header">Step 5: Content Hub Architecture</p>', unsafe_allow_html=True)
    st.markdown("Pillar + cluster content structure with internal linking")

    output = st.session_state.output
    hubs = output.content_hubs

    total_pages = sum(len(h.all_pages()) for h in hubs)
    total_links = sum(h.internal_link_count for h in hubs)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Content Hubs", len(hubs))
    with col2:
        st.metric("Total Pages", total_pages)
    with col3:
        st.metric("Internal Links", total_links)

    # Hub details
    st.markdown("### Hub Details")

    for hub in hubs:
        with st.expander(f"Hub: {hub.name} (Coverage: {hub.coverage_score:.0%})"):
            if hub.pillar_page:
                st.markdown(f"**Pillar:** {hub.pillar_page.title}")

            st.markdown("**Cluster Pages:**")
            for page in hub.cluster_pages:
                status = "✅" if page.status == "exists" else "📝"
                st.text(f"  {status} {page.title}")

            st.markdown(f"**Internal Links:** {hub.internal_link_count}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Queries"):
            st.session_state.step = 4
            st.rerun()
    with col2:
        if st.button("Next: Content Specs →", type="primary"):
            st.session_state.step = 6
            st.rerun()


def render_step_6_content():
    """Render Step 6: Content specifications."""
    st.markdown('<p class="step-header">Step 6: Content Specifications</p>', unsafe_allow_html=True)
    st.markdown("Detailed content specs with format, schema, and AI optimization")

    output = st.session_state.output
    specs = output.content_specs
    personas = output.personas

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Content Specs", len(specs))
    with col2:
        st.metric("Personas", len(personas))
    with col3:
        total_words = sum(s.word_count_target or 0 for s in specs)
        st.metric("Total Planned Words", f"{total_words:,}")

    # Personas
    st.markdown("### Target Personas")
    persona_cols = st.columns(len(personas))
    for i, persona in enumerate(personas):
        with persona_cols[i]:
            st.markdown(f"**{persona.name}**")
            st.caption(persona.knowledge_level)

    # Priority breakdown
    st.markdown("### Content by Priority")

    priority_counts = {}
    for spec in specs:
        p = spec.priority.value
        priority_counts[p] = priority_counts.get(p, 0) + 1

    st.bar_chart(priority_counts)

    # Top content specs
    st.markdown("### Critical Priority Content")

    critical = [s for s in specs if s.priority.value == "critical"]
    for spec in critical[:5]:
        with st.expander(spec.title):
            st.markdown(f"**Format:** {spec.recommended_format}")
            st.markdown(f"**Primary Query:** {spec.primary_query}")
            st.markdown(f"**Word Count:** {spec.word_count_target}")
            st.markdown("**Structure:**")
            for section in spec.content_structure[:5]:
                st.text(f"  • {section}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Hubs"):
            st.session_state.step = 5
            st.rerun()
    with col2:
        if st.button("Next: Measurement →", type="primary"):
            st.session_state.step = 7
            st.rerun()


def render_step_7_measurement():
    """Render Step 7: Measurement framework."""
    st.markdown('<p class="step-header">Step 7: Measurement Framework</p>', unsafe_allow_html=True)
    st.markdown("KPIs, AI monitoring, and content refresh schedules")

    output = st.session_state.output
    plan = output.measurement_plan

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("KPIs Defined", len(plan.kpis))
    with col2:
        st.metric("Monitoring Queries", len(plan.ai_monitoring_queries))
    with col3:
        st.metric("Competitors Tracked", len(plan.competitor_tracking))

    # KPIs
    st.markdown("### Key Performance Indicators")

    kpi_data = []
    for kpi in plan.kpis:
        kpi_data.append({
            "KPI": kpi.name,
            "Priority": kpi.priority,
            "Cadence": kpi.refresh_cadence,
        })

    st.dataframe(kpi_data, use_container_width=True)

    # AI Monitoring Queries
    st.markdown("### AI Monitoring Queries")
    st.markdown("Track these queries in ChatGPT, Perplexity, and AI Overviews:")

    for query in plan.ai_monitoring_queries[:10]:
        st.text(f"• {query}")

    # Refresh Schedule
    st.markdown("### Content Refresh Schedule")
    for content_type, cadence in plan.refresh_schedule.items():
        st.text(f"• {content_type}: {cadence}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Content"):
            st.session_state.step = 6
            st.rerun()
    with col2:
        if st.button("Export Roadmap →", type="primary"):
            st.session_state.step = 8
            st.rerun()


def render_export_step():
    """Render the export step."""
    st.markdown('<p class="step-header">Export Your Roadmap</p>', unsafe_allow_html=True)
    st.markdown("Download your AI visibility roadmap in various formats")

    output = st.session_state.output

    # Summary
    st.markdown("### Roadmap Summary")
    summary = output.summary

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Entities", summary.get("total_entities", 0))
    with col2:
        st.metric("Queries", summary.get("total_queries", 0))
    with col3:
        st.metric("Content Pages", summary.get("total_pages_planned", 0))
    with col4:
        st.metric("KPIs", summary.get("kpis_defined", 0))

    st.markdown("---")

    # Export options
    st.markdown("### Download Options")

    col1, col2 = st.columns(2)

    with col1:
        # JSON export
        json_data = Exporter.to_json(output)
        st.download_button(
            label="Download Complete JSON",
            data=json_data,
            file_name=f"{output.brand_name.lower().replace(' ', '_')}_roadmap.json",
            mime="application/json",
        )

        # Markdown export
        md_data = Exporter.to_markdown(output)
        st.download_button(
            label="Download Markdown Summary",
            data=md_data,
            file_name=f"{output.brand_name.lower().replace(' ', '_')}_roadmap.md",
            mime="text/markdown",
        )

    with col2:
        # CSV exports
        if output.ontology:
            entities_csv = Exporter.entities_to_csv(output.ontology)
            st.download_button(
                label="Download Entities CSV",
                data=entities_csv,
                file_name="entities.csv",
                mime="text/csv",
            )

        if output.query_clusters:
            queries_csv = Exporter.queries_to_csv(output.query_clusters)
            st.download_button(
                label="Download Queries CSV",
                data=queries_csv,
                file_name="queries.csv",
                mime="text/csv",
            )

        if output.content_hubs:
            hubs_csv = Exporter.content_hubs_to_csv(output.content_hubs)
            st.download_button(
                label="Download Content Plan CSV",
                data=hubs_csv,
                file_name="content_plan.csv",
                mime="text/csv",
            )

    st.markdown("---")

    # Quick wins
    st.markdown("### Recommended Next Steps")

    st.markdown("""
    1. **Review the ontology** - Validate entities and add any missing ones
    2. **Prioritize content creation** - Start with Critical priority pages
    3. **Implement schema markup** - Add structured data to existing pages
    4. **Set up AI monitoring** - Track brand mentions in ChatGPT/Perplexity
    5. **Create content calendar** - Plan content based on hub architecture
    """)

    if st.button("← Start Over", type="secondary"):
        st.session_state.step = 0
        st.session_state.config = None
        st.session_state.output = None
        st.rerun()


def main():
    """Main application entry point."""
    init_session_state()
    render_sidebar()

    # Handle processing state
    if st.session_state.processing:
        process_framework()
        return

    # Render appropriate step
    step = st.session_state.step

    if step == 0:
        render_configuration_step()
    elif step == 1:
        render_step_1_ontology()
    elif step == 2:
        render_step_2_entities()
    elif step == 3:
        render_step_3_taxonomy()
    elif step == 4:
        render_step_4_queries()
    elif step == 5:
        render_step_5_hubs()
    elif step == 6:
        render_step_6_content()
    elif step == 7:
        render_step_7_measurement()
    elif step == 8:
        render_export_step()


if __name__ == "__main__":
    main()
