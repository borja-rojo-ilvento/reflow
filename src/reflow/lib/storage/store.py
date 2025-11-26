"""Core storage operations for content management."""

from pathlib import Path
from typing import Any, Dict, Optional

from .indexes import update_indexes, query_by_hash
from .metadata import write_metadata, read_metadata, enrich_metadata, validate_metadata
from .utils import (
    compute_hash,
    get_short_hash,
    get_store_path,
    ensure_directory,
    content_exists,
    get_content_path,
    get_file_extension,
    resolve_hash_collision,
)


def store_content(
    content: bytes,
    content_type: str,
    metadata: Dict[str, Any],
    supplementary: Optional[Dict[str, bytes]] = None,
    base_path: Optional[str] = None
) -> str:
    """
    Store content with metadata and update indexes.

    Args:
        content: Raw bytes of content to store
        content_type: File extension (pdf, html, json, etc.)
        metadata: Dictionary of metadata fields (title, topics, date, etc.)
        supplementary: Optional dict of additional files {filename: bytes}
        base_path: Optional custom store base path

    Returns:
        Hash directory name where content was stored

    Raises:
        ValueError: If metadata validation fails

    Example:
        >>> hash_dir = store_content(
        ...     content=pdf_bytes,
        ...     content_type="pdf",
        ...     metadata={
        ...         "title": "Attention Is All You Need",
        ...         "topics": ["transformers", "attention"],
        ...         "date": "2025-11-15T08:00:00Z",
        ...         "source_type": "arxiv",
        ...         "source_url": "https://arxiv.org/abs/1706.03762",
        ...         "content_category": "academic-paper"
        ...     }
        ... )
    """
    # 1. Compute content hash
    full_hash = compute_hash(content)

    # 2. Check if content already exists (deduplication)
    existing_dir = find_content(content, base_path)
    if existing_dir:
        # Content already stored, return existing directory
        return existing_dir

    # 3. Prepare metadata
    content_filename = f"content.{content_type}"

    # Enrich metadata with computed fields
    enriched_metadata = enrich_metadata(metadata)
    enriched_metadata['content_hash'] = full_hash
    enriched_metadata['content_file'] = content_filename
    enriched_metadata['content_type'] = content_type

    # Validate metadata
    errors = validate_metadata(enriched_metadata)
    if errors:
        raise ValueError(f"Metadata validation failed: {', '.join(errors)}")

    # 4. Determine directory name (handle collisions)
    short_hash = get_short_hash(full_hash)
    hash_dir = short_hash

    store_path = get_store_path(base_path)

    # Check for hash collision
    if content_exists(short_hash, base_path):
        existing_metadata_path = get_content_path(short_hash, base_path) / "metadata.md"
        existing_metadata = read_metadata(existing_metadata_path)
        existing_hash = existing_metadata.get('content_hash')

        if existing_hash != full_hash:
            # Collision detected! Extend hash
            hash_dir = resolve_hash_collision(full_hash, existing_hash, len(short_hash))

    # 5. Create content directory
    content_dir = store_path / hash_dir
    ensure_directory(content_dir)

    # 6. Write content file
    content_file = content_dir / content_filename
    content_file.write_bytes(content)

    # 7. Write supplementary files if provided
    if supplementary:
        for filename, file_content in supplementary.items():
            supp_file = content_dir / filename
            supp_file.write_bytes(file_content)

    # 8. Write metadata.md
    metadata_file = content_dir / "metadata.md"
    write_metadata(metadata_file, enriched_metadata)

    # 9. Update indexes
    update_indexes(hash_dir, enriched_metadata, base_path)

    return hash_dir


def find_content(content: bytes, base_path: Optional[str] = None) -> Optional[str]:
    """
    Check if content already exists in store.

    Args:
        content: Raw bytes of content to check
        base_path: Optional custom store base path

    Returns:
        Hash directory name if found, None otherwise
    """
    full_hash = compute_hash(content)
    return query_by_hash(full_hash, base_path)


def get_content(hash_dir: str, base_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve content and metadata for a hash directory.

    Args:
        hash_dir: Hash-based directory name
        base_path: Optional custom store base path

    Returns:
        Dictionary containing:
        - metadata: All metadata fields including body
        - content_path: Path to content file
        - supplementary_files: List of additional file paths

    Raises:
        FileNotFoundError: If hash directory doesn't exist
    """
    content_path = get_content_path(hash_dir, base_path)

    if not content_path.exists():
        raise FileNotFoundError(f"Content directory not found: {hash_dir}")

    # Read metadata
    metadata_file = content_path / "metadata.md"
    metadata = read_metadata(metadata_file)

    # Find content file
    content_filename = metadata.get('content_file')
    if not content_filename:
        raise ValueError(f"Metadata missing content_file field: {hash_dir}")

    content_file_path = content_path / content_filename

    # Find supplementary files (anything other than metadata.md and content file)
    supplementary = []
    for file_path in content_path.iterdir():
        if file_path.is_file() and file_path.name not in ['metadata.md', content_filename]:
            supplementary.append(file_path)

    return {
        'metadata': metadata,
        'content_path': content_file_path,
        'supplementary_files': supplementary,
    }


def delete_content(hash_dir: str, base_path: Optional[str] = None) -> None:
    """
    Delete content directory and remove from indexes.

    Args:
        hash_dir: Hash-based directory name
        base_path: Optional custom store base path

    Note:
        This does NOT update indexes. Call rebuild_indexes() afterward
        if you need indexes to be accurate.
    """
    import shutil

    content_path = get_content_path(hash_dir, base_path)

    if content_path.exists():
        shutil.rmtree(content_path)


def list_all_content(base_path: Optional[str] = None) -> list[str]:
    """
    List all hash directories in store.

    Args:
        base_path: Optional custom store base path

    Returns:
        List of hash directory names
    """
    store_path = get_store_path(base_path)

    if not store_path.exists():
        return []

    return [d.name for d in store_path.iterdir() if d.is_dir()]
