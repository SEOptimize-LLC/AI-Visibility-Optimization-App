"""Sitemap parser for extracting URLs and content structure."""

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from urllib.parse import urlparse, urljoin
from typing import Any
import httpx


@dataclass
class SitemapURL:
    """Represents a URL from a sitemap."""
    loc: str
    lastmod: str | None = None
    changefreq: str | None = None
    priority: float | None = None
    path_segments: list[str] = field(default_factory=list)
    inferred_category: str | None = None
    inferred_entity: str | None = None


@dataclass
class SitemapAnalysis:
    """Analysis results from parsing a sitemap."""
    base_url: str
    total_urls: int
    urls: list[SitemapURL]
    categories: dict[str, int]  # category -> count
    content_types: dict[str, int]  # inferred type -> count
    url_patterns: list[str]
    errors: list[str]


class SitemapParser:
    """
    Parse XML sitemaps and extract structural information.

    Handles:
    - Standard XML sitemaps
    - Sitemap index files
    - URL path analysis for category/entity extraction
    """

    # Common URL path patterns that indicate content types
    CONTENT_TYPE_PATTERNS = {
        "blog": r"/(blog|articles?|posts?|news)/",
        "product": r"/(products?|shop|store|catalog)/",
        "category": r"/(category|categories|topics?)/",
        "tag": r"/(tags?)/",
        "author": r"/(authors?|team|people)/",
        "resource": r"/(resources?|guides?|tutorials?)/",
        "landing": r"/(landing|lp)/",
        "legal": r"/(privacy|terms|legal|policy)/",
        "support": r"/(support|help|faq|docs?)/",
    }

    # Words to ignore when extracting entities from URLs
    STOP_WORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
        "be", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "shall", "can", "need",
        "index", "page", "default", "home", "main", "about", "contact",
    }

    def __init__(self, timeout: float = 30.0):
        """Initialize parser with optional timeout."""
        self.timeout = timeout
        self._client: httpx.Client | None = None

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                timeout=self.timeout,
                follow_redirects=True,
                headers={"User-Agent": "AI-Visibility-Framework/1.0"}
            )
        return self._client

    def parse_sitemap(self, sitemap_url: str) -> SitemapAnalysis:
        """
        Parse a sitemap URL and return analysis.

        Handles both regular sitemaps and sitemap index files.
        """
        errors: list[str] = []
        all_urls: list[SitemapURL] = []

        try:
            content = self._fetch_sitemap(sitemap_url)
            root = ET.fromstring(content)

            # Detect namespace
            ns = self._extract_namespace(root)

            # Check if this is a sitemap index
            if root.tag.endswith("sitemapindex"):
                sitemap_locs = self._parse_sitemap_index(root, ns)
                for loc in sitemap_locs[:10]:  # Limit to prevent overload
                    try:
                        sub_content = self._fetch_sitemap(loc)
                        sub_root = ET.fromstring(sub_content)
                        sub_ns = self._extract_namespace(sub_root)
                        sub_urls = self._parse_urlset(sub_root, sub_ns)
                        all_urls.extend(sub_urls)
                    except Exception as e:
                        errors.append(f"Error parsing {loc}: {str(e)}")
            else:
                all_urls = self._parse_urlset(root, ns)

        except Exception as e:
            errors.append(f"Error parsing sitemap: {str(e)}")

        # Analyze URLs
        base_url = self._extract_base_url(sitemap_url)
        categories = self._analyze_categories(all_urls)
        content_types = self._analyze_content_types(all_urls)
        url_patterns = self._detect_url_patterns(all_urls)

        return SitemapAnalysis(
            base_url=base_url,
            total_urls=len(all_urls),
            urls=all_urls,
            categories=categories,
            content_types=content_types,
            url_patterns=url_patterns,
            errors=errors,
        )

    def _fetch_sitemap(self, url: str) -> str:
        """Fetch sitemap content."""
        client = self._get_client()
        response = client.get(url)
        response.raise_for_status()
        return response.text

    def _extract_namespace(self, root: ET.Element) -> dict[str, str]:
        """Extract XML namespace from root element."""
        match = re.match(r"\{(.+?)\}", root.tag)
        if match:
            return {"sm": match.group(1)}
        return {}

    def _parse_sitemap_index(
        self, root: ET.Element, ns: dict[str, str]
    ) -> list[str]:
        """Parse sitemap index and return list of sitemap URLs."""
        prefix = f"{{{ns.get('sm', '')}}}" if ns else ""
        locs = []
        for sitemap in root.findall(f".//{prefix}sitemap"):
            loc = sitemap.find(f"{prefix}loc")
            if loc is not None and loc.text:
                locs.append(loc.text.strip())
        return locs

    def _parse_urlset(
        self, root: ET.Element, ns: dict[str, str]
    ) -> list[SitemapURL]:
        """Parse urlset and return list of SitemapURL objects."""
        prefix = f"{{{ns.get('sm', '')}}}" if ns else ""
        urls = []

        for url_elem in root.findall(f".//{prefix}url"):
            loc = url_elem.find(f"{prefix}loc")
            if loc is None or not loc.text:
                continue

            lastmod = url_elem.find(f"{prefix}lastmod")
            changefreq = url_elem.find(f"{prefix}changefreq")
            priority = url_elem.find(f"{prefix}priority")

            sitemap_url = SitemapURL(
                loc=loc.text.strip(),
                lastmod=lastmod.text.strip() if lastmod is not None and lastmod.text else None,
                changefreq=changefreq.text.strip() if changefreq is not None and changefreq.text else None,
                priority=float(priority.text) if priority is not None and priority.text else None,
            )

            # Analyze path
            self._analyze_url_path(sitemap_url)
            urls.append(sitemap_url)

        return urls

    def _analyze_url_path(self, sitemap_url: SitemapURL):
        """Analyze URL path to extract segments, category, and potential entity."""
        parsed = urlparse(sitemap_url.loc)
        path = parsed.path.strip("/")

        if not path:
            return

        segments = path.split("/")
        sitemap_url.path_segments = segments

        # Infer category from first meaningful segment
        if segments:
            first_segment = segments[0].lower()
            # Check if it matches a known content type
            for content_type, pattern in self.CONTENT_TYPE_PATTERNS.items():
                if re.search(pattern, f"/{first_segment}/", re.IGNORECASE):
                    sitemap_url.inferred_category = content_type
                    break

            if not sitemap_url.inferred_category and len(first_segment) > 2:
                sitemap_url.inferred_category = first_segment

        # Infer entity from last segment (usually the page slug)
        if segments:
            last_segment = segments[-1]
            # Remove common file extensions
            last_segment = re.sub(r"\.(html?|php|aspx?)$", "", last_segment, flags=re.IGNORECASE)
            # Convert slug to readable text
            entity_text = last_segment.replace("-", " ").replace("_", " ")
            # Filter out stop words and short segments
            words = [w for w in entity_text.split() if w.lower() not in self.STOP_WORDS and len(w) > 2]
            if words:
                sitemap_url.inferred_entity = " ".join(words).title()

    def _extract_base_url(self, sitemap_url: str) -> str:
        """Extract base URL from sitemap URL."""
        parsed = urlparse(sitemap_url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _analyze_categories(self, urls: list[SitemapURL]) -> dict[str, int]:
        """Count URLs by inferred category."""
        categories: dict[str, int] = {}
        for url in urls:
            if url.inferred_category:
                cat = url.inferred_category
                categories[cat] = categories.get(cat, 0) + 1
        return dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))

    def _analyze_content_types(self, urls: list[SitemapURL]) -> dict[str, int]:
        """Analyze and count content types."""
        content_types: dict[str, int] = {}
        for url in urls:
            for content_type, pattern in self.CONTENT_TYPE_PATTERNS.items():
                if re.search(pattern, url.loc, re.IGNORECASE):
                    content_types[content_type] = content_types.get(content_type, 0) + 1
                    break
            else:
                content_types["other"] = content_types.get("other", 0) + 1
        return dict(sorted(content_types.items(), key=lambda x: x[1], reverse=True))

    def _detect_url_patterns(self, urls: list[SitemapURL]) -> list[str]:
        """Detect common URL patterns in the sitemap."""
        patterns: dict[str, int] = {}

        for url in urls:
            if not url.path_segments:
                continue

            # Create pattern by replacing specific values with placeholders
            pattern_parts = []
            for segment in url.path_segments:
                if re.match(r"^\d+$", segment):
                    pattern_parts.append("{id}")
                elif re.match(r"^\d{4}$", segment):
                    pattern_parts.append("{year}")
                elif re.match(r"^\d{1,2}$", segment):
                    pattern_parts.append("{month}")
                elif len(segment) > 30:
                    pattern_parts.append("{slug}")
                else:
                    pattern_parts.append(segment)

            pattern = "/" + "/".join(pattern_parts)
            patterns[pattern] = patterns.get(pattern, 0) + 1

        # Return top patterns
        sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
        return [p[0] for p in sorted_patterns[:20]]

    def extract_entities_from_sitemap(self, sitemap_url: str) -> list[dict[str, Any]]:
        """
        Extract potential entities from sitemap URLs.

        Returns list of entity candidates with frequency and source URLs.
        """
        analysis = self.parse_sitemap(sitemap_url)
        entity_counts: dict[str, dict[str, Any]] = {}

        for url in analysis.urls:
            if url.inferred_entity:
                entity_lower = url.inferred_entity.lower()
                if entity_lower not in entity_counts:
                    entity_counts[entity_lower] = {
                        "name": url.inferred_entity,
                        "count": 0,
                        "source_urls": [],
                        "categories": set(),
                    }
                entity_counts[entity_lower]["count"] += 1
                entity_counts[entity_lower]["source_urls"].append(url.loc)
                if url.inferred_category:
                    entity_counts[entity_lower]["categories"].add(url.inferred_category)

        # Convert to list and sort by frequency
        entities = []
        for data in entity_counts.values():
            entities.append({
                "name": data["name"],
                "frequency": data["count"],
                "source_urls": data["source_urls"][:5],  # Limit URLs
                "categories": list(data["categories"]),
            })

        entities.sort(key=lambda x: x["frequency"], reverse=True)
        return entities[:100]  # Return top 100

    def close(self):
        """Close HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
