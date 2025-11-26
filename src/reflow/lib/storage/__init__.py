"""Storage system for content management with hash-based deduplication."""

from .store import store_content, find_content
from .metadata import write_metadata, read_metadata, update_metadata
from .indexes import (
    update_indexes,
    query_by_topic,
    query_by_date,
    query_by_type,
    rebuild_indexes,
)
from .utils import compute_hash, get_short_hash

__all__ = [
    "store_content",
    "find_content",
    "write_metadata",
    "read_metadata",
    "update_metadata",
    "update_indexes",
    "query_by_topic",
    "query_by_date",
    "query_by_type",
    "rebuild_indexes",
    "compute_hash",
    "get_short_hash",
]
