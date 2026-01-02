"""Input validation utilities for the AI Search Visibility Framework."""

import re
from urllib.parse import urlparse
from typing import Any

from config.templates import BrandFoundationConfig, SourceMode


class ValidationError:
    """Represents a validation error."""

    def __init__(self, field: str, message: str, severity: str = "error"):
        self.field = field
        self.message = message
        self.severity = severity  # "error", "warning", "info"

    def __str__(self):
        return f"[{self.severity.upper()}] {self.field}: {self.message}"


class InputValidator:
    """
    Validate user inputs for the framework.

    Provides comprehensive validation with helpful error messages.
    """

    # URL validation pattern
    URL_PATTERN = re.compile(
        r"^https?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    # Sitemap-specific patterns
    SITEMAP_EXTENSIONS = [".xml", "sitemap", "sitemap.xml", "sitemap_index.xml"]

    # Entity name constraints
    MIN_ENTITY_LENGTH = 2
    MAX_ENTITY_LENGTH = 100
    MIN_ENTITIES = 1
    MAX_ENTITIES = 50

    # Brand name constraints
    MIN_BRAND_LENGTH = 1
    MAX_BRAND_LENGTH = 100

    @classmethod
    def validate_config(cls, config: BrandFoundationConfig) -> list[ValidationError]:
        """
        Validate complete brand foundation configuration.

        Returns list of validation errors (empty if valid).
        """
        errors = []

        # Brand name validation
        errors.extend(cls.validate_brand_name(config.brand_name))

        # Niche validation
        errors.extend(cls.validate_niche(config.primary_niche))

        # Business goals validation
        if not config.business_goals:
            errors.append(ValidationError(
                "business_goals",
                "At least one business goal must be selected"
            ))

        # Source mode specific validation
        if config.source_mode == SourceMode.SITEMAP:
            errors.extend(cls.validate_sitemap_url(config.sitemap_url))
        elif config.source_mode == SourceMode.SEED:
            errors.extend(cls.validate_seed_entities(config.seed_entities))
        elif config.source_mode == SourceMode.HYBRID:
            # Hybrid requires at least one of sitemap or seed entities
            has_sitemap = config.sitemap_url and cls.is_valid_url(config.sitemap_url)
            has_seeds = config.seed_entities and len(config.seed_entities) > 0
            if not has_sitemap and not has_seeds:
                errors.append(ValidationError(
                    "source_mode",
                    "Hybrid mode requires either a sitemap URL or seed entities"
                ))

        # Competitors validation (optional but validate if provided)
        for i, competitor in enumerate(config.competitors):
            if competitor.strip() and len(competitor.strip()) < cls.MIN_ENTITY_LENGTH:
                errors.append(ValidationError(
                    f"competitors[{i}]",
                    f"Competitor name too short (min {cls.MIN_ENTITY_LENGTH} chars)",
                    severity="warning"
                ))

        return errors

    @classmethod
    def validate_brand_name(cls, brand_name: str | None) -> list[ValidationError]:
        """Validate brand name input."""
        errors = []

        if not brand_name:
            errors.append(ValidationError("brand_name", "Brand name is required"))
            return errors

        brand_name = brand_name.strip()

        if len(brand_name) < cls.MIN_BRAND_LENGTH:
            errors.append(ValidationError(
                "brand_name",
                f"Brand name must be at least {cls.MIN_BRAND_LENGTH} character(s)"
            ))

        if len(brand_name) > cls.MAX_BRAND_LENGTH:
            errors.append(ValidationError(
                "brand_name",
                f"Brand name must be less than {cls.MAX_BRAND_LENGTH} characters"
            ))

        # Check for problematic characters
        if re.search(r"[<>\"'&]", brand_name):
            errors.append(ValidationError(
                "brand_name",
                "Brand name contains invalid characters",
                severity="warning"
            ))

        return errors

    @classmethod
    def validate_niche(cls, niche: str | None) -> list[ValidationError]:
        """Validate primary niche input."""
        errors = []

        if not niche:
            errors.append(ValidationError("primary_niche", "Primary niche is required"))
            return errors

        niche = niche.strip()

        if len(niche) < 3:
            errors.append(ValidationError(
                "primary_niche",
                "Niche description should be at least 3 characters"
            ))

        if len(niche) > 200:
            errors.append(ValidationError(
                "primary_niche",
                "Niche description should be less than 200 characters",
                severity="warning"
            ))

        return errors

    @classmethod
    def validate_sitemap_url(cls, url: str | None) -> list[ValidationError]:
        """Validate sitemap URL."""
        errors = []

        if not url:
            errors.append(ValidationError(
                "sitemap_url",
                "Sitemap URL is required when using sitemap mode"
            ))
            return errors

        url = url.strip()

        if not cls.is_valid_url(url):
            errors.append(ValidationError(
                "sitemap_url",
                "Invalid URL format. Must be a valid HTTP/HTTPS URL"
            ))
            return errors

        # Check if URL looks like a sitemap
        is_sitemap = any(ext in url.lower() for ext in cls.SITEMAP_EXTENSIONS)
        if not is_sitemap:
            errors.append(ValidationError(
                "sitemap_url",
                "URL doesn't appear to be a sitemap (expected .xml extension)",
                severity="warning"
            ))

        return errors

    @classmethod
    def validate_seed_entities(cls, entities: list[str] | None) -> list[ValidationError]:
        """Validate seed entities list."""
        errors = []

        if not entities:
            errors.append(ValidationError(
                "seed_entities",
                "At least one seed entity is required when using seed mode"
            ))
            return errors

        if len(entities) < cls.MIN_ENTITIES:
            errors.append(ValidationError(
                "seed_entities",
                f"At least {cls.MIN_ENTITIES} seed entity is required"
            ))

        if len(entities) > cls.MAX_ENTITIES:
            errors.append(ValidationError(
                "seed_entities",
                f"Maximum {cls.MAX_ENTITIES} seed entities allowed",
                severity="warning"
            ))

        # Validate individual entities
        for i, entity in enumerate(entities):
            entity = entity.strip() if entity else ""

            if not entity:
                errors.append(ValidationError(
                    f"seed_entities[{i}]",
                    "Empty entity found"
                ))
                continue

            if len(entity) < cls.MIN_ENTITY_LENGTH:
                errors.append(ValidationError(
                    f"seed_entities[{i}]",
                    f"Entity '{entity}' is too short (min {cls.MIN_ENTITY_LENGTH} chars)"
                ))

            if len(entity) > cls.MAX_ENTITY_LENGTH:
                errors.append(ValidationError(
                    f"seed_entities[{i}]",
                    f"Entity '{entity}' is too long (max {cls.MAX_ENTITY_LENGTH} chars)"
                ))

        # Check for duplicates
        normalized = [e.lower().strip() for e in entities if e]
        if len(normalized) != len(set(normalized)):
            errors.append(ValidationError(
                "seed_entities",
                "Duplicate entities detected",
                severity="warning"
            ))

        return errors

    @classmethod
    def validate_url(cls, url: str, field_name: str = "url") -> list[ValidationError]:
        """Validate a generic URL."""
        errors = []

        if not url:
            errors.append(ValidationError(field_name, "URL is required"))
            return errors

        if not cls.is_valid_url(url.strip()):
            errors.append(ValidationError(
                field_name,
                "Invalid URL format"
            ))

        return errors

    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        """Check if string is a valid URL."""
        if not url:
            return False
        try:
            result = urlparse(url)
            return all([result.scheme in ("http", "https"), result.netloc])
        except Exception:
            return False

    @classmethod
    def sanitize_entity(cls, entity: str) -> str:
        """Sanitize entity name for safe usage."""
        if not entity:
            return ""

        # Strip whitespace
        entity = entity.strip()

        # Remove dangerous characters
        entity = re.sub(r"[<>\"'&\\]", "", entity)

        # Normalize whitespace
        entity = re.sub(r"\s+", " ", entity)

        return entity

    @classmethod
    def sanitize_entities(cls, entities: list[str]) -> list[str]:
        """Sanitize list of entities."""
        sanitized = []
        for entity in entities:
            clean = cls.sanitize_entity(entity)
            if clean and len(clean) >= cls.MIN_ENTITY_LENGTH:
                sanitized.append(clean)
        return list(dict.fromkeys(sanitized))  # Remove duplicates while preserving order

    @classmethod
    def has_errors(cls, errors: list[ValidationError]) -> bool:
        """Check if error list contains any actual errors (not warnings)."""
        return any(e.severity == "error" for e in errors)

    @classmethod
    def format_errors(cls, errors: list[ValidationError]) -> str:
        """Format errors as readable string."""
        if not errors:
            return "No validation errors"

        lines = []
        actual_errors = [e for e in errors if e.severity == "error"]
        warnings = [e for e in errors if e.severity == "warning"]

        if actual_errors:
            lines.append("Errors:")
            for err in actual_errors:
                lines.append(f"  - {err.field}: {err.message}")

        if warnings:
            lines.append("Warnings:")
            for warn in warnings:
                lines.append(f"  - {warn.field}: {warn.message}")

        return "\n".join(lines)
