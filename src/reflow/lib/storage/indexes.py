"""Index management for content retrieval."""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from .metadata import read_metadata
from .utils import get_indexes_path, get_store_path, ensure_directory


def _load_index(index_name: str, base_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load index from JSON file.

    Args:
        index_name: Name of index file (e.g., "by-topic")
        base_path: Optional custom indexes base path

    Returns:
        Dictionary of index data
    """
    indexes_path = get_indexes_path(base_path)
    index_file = indexes_path / f"{index_name}.json"

    if not index_file.exists():
        return {}

    with index_file.open('r', encoding='utf-8') as f:
        return json.load(f)


def _save_index(index_name: str, data: Dict[str, Any], base_path: Optional[str] = None) -> None:
    """
    Save index to JSON file.

    Args:
        index_name: Name of index file (e.g., "by-topic")
        data: Dictionary of index data
        base_path: Optional custom indexes base path
    """
    indexes_path = get_indexes_path(base_path)
    ensure_directory(indexes_path)

    index_file = indexes_path / f"{index_name}.json"

    with index_file.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def update_indexes(hash_dir: str, metadata: Dict[str, Any], base_path: Optional[str] = None) -> None:
    """
    Update all indexes for a newly stored piece of content.

    Args:
        hash_dir: Hash-based directory name
        metadata: Metadata dictionary for the content
        base_path: Optional custom base path for indexes
    """
    # Update by-hash index
    hash_index = _load_index("by-hash", base_path)
    hash_index[metadata['content_hash']] = hash_dir
    _save_index("by-hash", hash_index, base_path)

    # Update by-topic index
    topic_index = _load_index("by-topic", base_path)
    for topic in metadata.get('topics', []):
        if topic not in topic_index:
            topic_index[topic] = []
        if hash_dir not in topic_index[topic]:
            topic_index[topic].append(hash_dir)
    _save_index("by-topic", topic_index, base_path)

    # Update by-date index (organized by year/month)
    date_index = _load_index("by-date", base_path)
    year = metadata.get('year')
    if year:
        year_str = str(year)
        if year_str not in date_index:
            date_index[year_str] = {}

        # Try to extract month from date field
        date_str = metadata.get('date', '')
        month = None
        if date_str and len(date_str) >= 7:
            try:
                month = int(date_str[5:7])  # Extract MM from YYYY-MM-DD
            except (ValueError, IndexError):
                pass

        if month:
            month_str = str(month)
            if month_str not in date_index[year_str]:
                date_index[year_str][month_str] = []
            if hash_dir not in date_index[year_str][month_str]:
                date_index[year_str][month_str].append(hash_dir)
        else:
            # Add to year level if no month available
            if '_all' not in date_index[year_str]:
                date_index[year_str]['_all'] = []
            if hash_dir not in date_index[year_str]['_all']:
                date_index[year_str]['_all'].append(hash_dir)

    _save_index("by-date", date_index, base_path)

    # Update by-type index
    type_index = _load_index("by-type", base_path)
    source_type = metadata.get('source_type')
    if source_type:
        if source_type not in type_index:
            type_index[source_type] = []
        if hash_dir not in type_index[source_type]:
            type_index[source_type].append(hash_dir)
    _save_index("by-type", type_index, base_path)


def query_by_topic(topics: List[str], base_path: Optional[str] = None) -> List[str]:
    """
    Query content by topics.

    Args:
        topics: List of topic keywords
        base_path: Optional custom indexes base path

    Returns:
        List of hash directory names matching any of the topics
    """
    topic_index = _load_index("by-topic", base_path)
    results = set()

    for topic in topics:
        if topic in topic_index:
            results.update(topic_index[topic])

    return sorted(list(results))


def query_by_date(year: int, month: Optional[int] = None, base_path: Optional[str] = None) -> List[str]:
    """
    Query content by date.

    Args:
        year: Year to query
        month: Optional month (1-12)
        base_path: Optional custom indexes base path

    Returns:
        List of hash directory names for the time period
    """
    date_index = _load_index("by-date", base_path)
    year_str = str(year)

    if year_str not in date_index:
        return []

    if month is not None:
        month_str = str(month)
        return date_index[year_str].get(month_str, [])
    else:
        # Return all entries for the year
        results = set()
        for month_data in date_index[year_str].values():
            if isinstance(month_data, list):
                results.update(month_data)
        return sorted(list(results))


def query_by_type(source_type: str, base_path: Optional[str] = None) -> List[str]:
    """
    Query content by source type.

    Args:
        source_type: Source type (arxiv, twitter, reddit, etc.)
        base_path: Optional custom indexes base path

    Returns:
        List of hash directory names for the source type
    """
    type_index = _load_index("by-type", base_path)
    return type_index.get(source_type, [])


def query_by_hash(content_hash: str, base_path: Optional[str] = None) -> Optional[str]:
    """
    Query content by full hash.

    Args:
        content_hash: Full SHA-256 hash
        base_path: Optional custom indexes base path

    Returns:
        Hash directory name if found, None otherwise
    """
    hash_index = _load_index("by-hash", base_path)
    return hash_index.get(content_hash)


def rebuild_indexes(base_path: Optional[str] = None) -> None:
    """
    Rebuild all indexes from metadata.md files in store.

    Args:
        base_path: Optional custom base path

    This is useful for recovery or when indexes get out of sync.
    """
    store_path = get_store_path(base_path)

    # Initialize empty indexes
    hash_index = {}
    topic_index = defaultdict(list)
    date_index = defaultdict(lambda: defaultdict(list))
    type_index = defaultdict(list)

    # Scan all directories in store
    if not store_path.exists():
        return

    for content_dir in store_path.iterdir():
        if not content_dir.is_dir():
            continue

        metadata_file = content_dir / "metadata.md"
        if not metadata_file.exists():
            continue

        try:
            metadata = read_metadata(metadata_file)
            hash_dir = content_dir.name

            # Rebuild hash index
            content_hash = metadata.get('content_hash')
            if content_hash:
                hash_index[content_hash] = hash_dir

            # Rebuild topic index
            for topic in metadata.get('topics', []):
                if hash_dir not in topic_index[topic]:
                    topic_index[topic].append(hash_dir)

            # Rebuild date index
            year = metadata.get('year')
            if year:
                year_str = str(year)
                date_str = metadata.get('date', '')
                month = None
                if date_str and len(date_str) >= 7:
                    try:
                        month = int(date_str[5:7])
                    except (ValueError, IndexError):
                        pass

                if month:
                    month_str = str(month)
                    if hash_dir not in date_index[year_str][month_str]:
                        date_index[year_str][month_str].append(hash_dir)
                else:
                    if hash_dir not in date_index[year_str]['_all']:
                        date_index[year_str]['_all'].append(hash_dir)

            # Rebuild type index
            source_type = metadata.get('source_type')
            if source_type and hash_dir not in type_index[source_type]:
                type_index[source_type].append(hash_dir)

        except Exception as e:
            # Skip problematic metadata files
            print(f"Warning: Could not process {metadata_file}: {e}")
            continue

    # Save all indexes
    _save_index("by-hash", hash_index, base_path)
    _save_index("by-topic", dict(topic_index), base_path)
    _save_index("by-date", {k: dict(v) for k, v in date_index.items()}, base_path)
    _save_index("by-type", dict(type_index), base_path)


def get_index_stats(base_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Get statistics about the indexes.

    Args:
        base_path: Optional custom base path

    Returns:
        Dictionary with index statistics
    """
    hash_index = _load_index("by-hash", base_path)
    topic_index = _load_index("by-topic", base_path)
    date_index = _load_index("by-date", base_path)
    type_index = _load_index("by-type", base_path)

    return {
        'total_content': len(hash_index),
        'total_topics': len(topic_index),
        'total_years': len(date_index),
        'total_source_types': len(type_index),
        'topics': list(topic_index.keys()),
        'years': list(date_index.keys()),
        'source_types': list(type_index.keys()),
    }
