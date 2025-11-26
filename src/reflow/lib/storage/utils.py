"""Utility functions for storage operations."""

import hashlib
import os
import re
import unicodedata
from pathlib import Path
from typing import Optional


def compute_hash(content: bytes) -> str:
    """
    Compute SHA-256 hash of content.

    Args:
        content: Raw bytes of content to hash

    Returns:
        Hexadecimal string representation of SHA-256 hash
    """
    return hashlib.sha256(content).hexdigest()


def get_short_hash(full_hash: str, length: int = 8) -> str:
    """
    Get shortened version of hash for directory naming.

    Args:
        full_hash: Full hexadecimal hash string
        length: Number of characters to use (default: 8)

    Returns:
        First `length` characters of hash
    """
    return full_hash[:length]


def get_store_path(base_path: Optional[str] = None) -> Path:
    """
    Get the base store directory path.

    Args:
        base_path: Optional custom base path. If None, uses ./store

    Returns:
        Path object for store directory
    """
    if base_path is None:
        base_path = os.path.join(os.getcwd(), "store")
    return Path(base_path)


def get_indexes_path(base_path: Optional[str] = None) -> Path:
    """
    Get the indexes directory path.

    Args:
        base_path: Optional custom base path. If None, uses ./indexes

    Returns:
        Path object for indexes directory
    """
    if base_path is None:
        base_path = os.path.join(os.getcwd(), "indexes")
    return Path(base_path)


def ensure_directory(path: Path) -> None:
    """
    Ensure directory exists, creating it if necessary.

    Args:
        path: Path object for directory to create
    """
    path.mkdir(parents=True, exist_ok=True)


def content_exists(hash_dir: str, base_path: Optional[str] = None) -> bool:
    """
    Check if content directory exists in store.

    Args:
        hash_dir: Hash-based directory name (e.g., "a3f2e1b4")
        base_path: Optional custom store base path

    Returns:
        True if directory exists, False otherwise
    """
    store_path = get_store_path(base_path)
    content_path = store_path / hash_dir
    return content_path.exists() and content_path.is_dir()


def get_content_path(hash_dir: str, base_path: Optional[str] = None) -> Path:
    """
    Get full path to content directory.

    Args:
        hash_dir: Hash-based directory name
        base_path: Optional custom store base path

    Returns:
        Path object for content directory
    """
    store_path = get_store_path(base_path)
    return store_path / hash_dir


def get_file_extension(filename: str) -> str:
    """
    Extract file extension from filename.

    Args:
        filename: Name of file

    Returns:
        Extension without dot (e.g., "pdf", "html")
    """
    return Path(filename).suffix.lstrip('.')


def slugify(text: str, max_length: int = 60) -> str:
    """
    Convert text to URL-safe slug (for human-readable references).

    Args:
        text: Input text to slugify
        max_length: Maximum length of slug

    Returns:
        Slugified string

    Example:
        >>> slugify("Attention Is All You Need")
        'attention-is-all-you-need'
    """
    # Normalize unicode (é → e)
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')

    # Lowercase, replace spaces, remove special chars
    text = text.lower()
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'[^a-z0-9-]', '', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')

    # Truncate on word boundary
    if len(text) > max_length:
        text = text[:max_length].rsplit('-', 1)[0]

    return text


def resolve_hash_collision(
    full_hash: str,
    existing_hash: str,
    current_length: int = 8
) -> str:
    """
    Resolve hash collision by extending hash length.

    Args:
        full_hash: Full hash of new content
        existing_hash: Full hash of existing content
        current_length: Current hash prefix length

    Returns:
        Extended hash prefix that doesn't collide
    """
    # Try extending by 4 characters at a time
    for new_length in [12, 16, 20, 32, 64]:
        if new_length <= current_length:
            continue
        new_prefix = full_hash[:new_length]
        existing_prefix = existing_hash[:new_length]
        if new_prefix != existing_prefix:
            return new_prefix

    # If we get here, use full hash (should never happen with SHA-256)
    return full_hash
