"""Metadata handling for content storage."""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def _serialize_frontmatter(data: Dict[str, Any]) -> str:
    """
    Serialize dictionary to YAML frontmatter format.

    Args:
        data: Dictionary of metadata fields

    Returns:
        YAML string with frontmatter delimiters
    """
    yaml_content = yaml.dump(
        data, default_flow_style=False, sort_keys=False, allow_unicode=True
    )
    return f"---\n{yaml_content}---\n"


def _parse_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """
    Parse YAML frontmatter and body from metadata.md content.

    Args:
        content: Full content of metadata.md file

    Returns:
        Tuple of (frontmatter_dict, body_markdown)
    """
    # Match YAML frontmatter between --- delimiters
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        # No frontmatter found, treat entire content as body
        return {}, content

    yaml_content = match.group(1)
    body = match.group(2).strip()

    # Parse YAML
    frontmatter = yaml.safe_load(yaml_content) or {}

    return frontmatter, body


def generate_body_template(content_category: str = "other") -> str:
    """
    Generate markdown body template based on content category.

    Args:
        content_category: Type of content (academic-paper, tweet, etc.)

    Returns:
        Markdown template string
    """
    base_template = """# Summary

[2-3 sentence executive summary of the content]

# Key Findings

- [Important takeaway or claim 1]
- [Important takeaway or claim 2]
- [Important conclusion or insight]

# Content Context

**Type**: [e.g., Peer-reviewed academic paper, Preprint, Blog post, Tweet thread]
**Format**: [e.g., PDF with 12 pages, JSON with 47 tweets, MP4 video 45 minutes]
**Quality**: [e.g., Peer-reviewed, Preprint, Social media, Primary source]
**Relevance**: [Why this was collected, what research question it addresses]
"""
    return base_template


def write_metadata(
    file_path: Path, metadata: Dict[str, Any], body: Optional[str] = None
) -> None:
    """
    Write metadata.md file with YAML frontmatter and markdown body.

    Args:
        file_path: Path to metadata.md file
        metadata: Dictionary of metadata fields
        body: Optional markdown body content. If None, uses template.
    """
    # Generate frontmatter
    frontmatter = _serialize_frontmatter(metadata)

    # Generate or use provided body
    if body is None:
        body = generate_body_template(metadata.get("content_category", "other"))

    # Write file
    full_content = frontmatter + "\n" + body
    file_path.write_text(full_content, encoding="utf-8")


def read_metadata(file_path: Path) -> Dict[str, Any]:
    """
    Read and parse metadata.md file.

    Args:
        file_path: Path to metadata.md file

    Returns:
        Dictionary containing:
        - All frontmatter fields
        - 'body': markdown body content
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {file_path}")

    content = file_path.read_text(encoding="utf-8")
    frontmatter, body = _parse_frontmatter(content)

    # Include body in returned dict
    result = dict(frontmatter)
    result["body"] = body

    return result


def update_metadata(
    file_path: Path,
    updates: Optional[Dict[str, Any]] = None,
    body_append: Optional[str] = None,
) -> None:
    """
    Update metadata.md file by modifying frontmatter fields or appending to body.

    Args:
        file_path: Path to metadata.md file
        updates: Optional dictionary of frontmatter fields to update
        body_append: Optional markdown content to append to body
    """
    # Read existing metadata
    metadata = read_metadata(file_path)
    body = metadata.pop("body", "")

    # Apply updates to frontmatter
    if updates:
        metadata.update(updates)

    # Append to body if provided
    if body_append:
        body = body.rstrip() + "\n\n" + body_append

    # Write back
    write_metadata(file_path, metadata, body)


def validate_metadata(metadata: Dict[str, Any]) -> list[str]:
    """
    Validate metadata against schema requirements.

    Args:
        metadata: Dictionary of metadata fields

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Required fields
    required = [
        "content_hash",
        "content_file",
        "title",
        "content_type",
        "content_category",
        "topics",
        "date",
        "source_type",
        "source_url",
    ]

    for field in required:
        if field not in metadata:
            errors.append(f"Missing required field: {field}")

    # Type validations
    if "topics" in metadata and not isinstance(metadata["topics"], list):
        errors.append("Field 'topics' must be a list")

    if "year" in metadata and not isinstance(metadata["year"], int):
        errors.append("Field 'year' must be an integer")

    # Enum validations
    valid_content_types = ["pdf", "html", "json", "mp4", "md", "txt", "xml", "zip"]
    if (
        "content_type" in metadata
        and metadata["content_type"] not in valid_content_types
    ):
        errors.append(f"Invalid content_type: {metadata['content_type']}")

    valid_categories = [
        "academic-paper",
        "financial-report",
        "tweet",
        "tweet-thread",
        "reddit-thread",
        "blog-post",
        "video",
        "lecture",
        "documentation",
        "news-article",
        "other",
    ]
    if (
        "content_category" in metadata
        and metadata["content_category"] not in valid_categories
    ):
        errors.append(f"Invalid content_category: {metadata['content_category']}")

    return errors


def enrich_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich metadata by deriving additional fields.

    Args:
        metadata: Base metadata dictionary

    Returns:
        Enriched metadata with derived fields
    """
    enriched = dict(metadata)

    # Extract year from date if not present
    if "date" in metadata and "year" not in enriched:
        try:
            date_obj = datetime.fromisoformat(metadata["date"].replace("Z", "+00:00"))
            enriched["year"] = date_obj.year
        except (ValueError, AttributeError):
            pass

    # Set default empty lists for optional array fields
    for field in ["tags", "keywords", "authors"]:
        if field not in enriched:
            enriched[field] = []

    return enriched
