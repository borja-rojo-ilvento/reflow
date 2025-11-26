---
id: doc-3
title: Storage-Achitecture
type: other
created_date: '2025-11-21 05:30'
---
# Storage Architecture

## Structure

```
store/
├── a3f2e1b4/           # Hash-based directories (first 8 chars of SHA-256)
│   ├── metadata.md
│   └── content.html
│
├── b7c4d9a2/
│   ├── metadata.md
│   └── content.pdf
│
├── c8d5e0f1/
│   ├── metadata.md
│   ├── content.mp4
│   └── transcript.md   # Supplementary files

lib/
├── schemas/
│   ├── metadata.schema.yaml       # Base metadata schema
│   ├── arxiv-paper.schema.yaml
│   ├── tweet.schema.yaml
│   └── reddit-thread.schema.yaml
│
└── storage/
    ├── __init__.py
    ├── store.py        # Core storage operations
    ├── metadata.py     # Frontmatter handling
    ├── indexes.py      # Index management
    └── utils.py        # Hash computation, path utilities

indexes/
├── by-topic.json       # {"llm": ["a3f2e1b4", ...], ...}
├── by-type.json        # {"arxiv": ["a3f2e1b4", ...], ...}
├── by-date.json        # {"2025": {"11": ["a3f2e1b4", ...]}, ...}
└── by-hash.json        # {"<full-hash>": "a3f2e1b4", ...}
```

## Design Principles

- **Content-addressed storage**: Directory names are hash-based for guaranteed uniqueness
- **Flat structure**: Minimize hierarchy to maintain flexibility
- **Differentiation by inspection**: Metadata describes content type, not file paths
- **Schema-driven**: Self-describing type definitions in `lib/schemas/`
- **Indexes are derived**: Can be rebuilt from `metadata.md` files
- **Progressive disclosure**: Metadata body provides layered information (summary, findings, context)
- **Extensible**: Schema designed to accommodate future features (vector search, embeddings)

## Key Components

### Store Directories

Each piece of content is stored in a hash-based directory (first 8 characters of SHA-256):
- `metadata.md`: YAML frontmatter + markdown notes
- `content.{ext}`: Original content file (html, pdf, mp4, etc.)
- Additional files as needed (e.g., `transcript.md` for videos)

Hash collision handling: If a collision occurs (extremely rare), the hash prefix is extended to 12 or 16 characters.

### Hash Index (`indexes/by-hash.json`)

Maps full content hash to hash-based directory for deduplication:

```json
{
  "a3f2e1b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2": "a3f2e1b4",
  "b7c4d9a2e3f1g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f3": "b7c4d9a2"
}
```

### Metadata Format (`metadata.md`)

```markdown
---
# Core identification
content_hash: a3f2e1b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2
content_file: content.pdf
title: "Attention Is All You Need"

# Content typing
content_type: pdf
content_category: academic-paper
schema_type: arxiv-paper
schema_ref: lib/schemas/arxiv-paper.schema.yaml

# Topic/taxonomy indexing
topics:
  - transformers
  - attention
  - deep-learning
tags:
  - nlp
  - architecture
keywords:
  - self-attention
  - encoder-decoder

# Temporal indexing
date: 2025-11-15T08:00:00Z
published_date: 2017-06-12
year: 2025

# Source metadata
source_type: arxiv
source_url: https://arxiv.org/abs/1706.03762
authors:
  - Vaswani A
  - Shazeer N
  - Parmar N
venue: NeurIPS 2017
---

# Summary

The seminal paper introducing the Transformer architecture, which relies entirely on self-attention mechanisms without recurrence or convolution. Demonstrates state-of-the-art results on machine translation tasks.

# Key Findings

- Self-attention can replace recurrent and convolutional layers entirely
- Multi-head attention allows modeling different representation subspaces
- Positional encodings enable the model to use sequence order information
- Achieves better BLEU scores on translation with significantly less training time

# Content Context

**Type**: Peer-reviewed academic paper
**Format**: PDF with 15 pages
**Quality**: Peer-reviewed, published at NeurIPS 2017
**Relevance**: Foundational architecture for modern LLMs and transformers
```

## Deduplication

Hash-based storage provides automatic deduplication:
1. Compute content hash (SHA-256)
2. Look up in `indexes/by-hash.json`
3. If found: content already exists, return existing hash directory
4. If not found: create new directory with hash prefix

## Storage API

### Core Functions

```python
from lib.storage import store_content, find_content, get_content

# Store new content
hash_dir = store_content(
    content=pdf_bytes,
    content_type="pdf",
    metadata={
        "title": "Attention Is All You Need",
        "topics": ["transformers", "attention"],
        "date": "2025-11-15T08:00:00Z",
        "source_type": "arxiv",
        "source_url": "https://arxiv.org/abs/1706.03762",
        "content_category": "academic-paper"
    },
    supplementary={"transcript.md": transcript_bytes}  # Optional
)
# Returns: "a3f2e1b4"

# Check if content exists
existing_dir = find_content(pdf_bytes)
# Returns: "a3f2e1b4" or None

# Retrieve content
data = get_content("a3f2e1b4")
# Returns: {
#   'metadata': {...},
#   'content_path': Path('store/a3f2e1b4/content.pdf'),
#   'supplementary_files': [Path(...)]
# }
```

### Query Functions

```python
from lib.storage import query_by_topic, query_by_date, query_by_type

# Query by topics
results = query_by_topic(["transformers", "attention"])
# Returns: ["a3f2e1b4", "c8d5e0f1", ...]

# Query by date
results = query_by_date(year=2025, month=11)
# Returns: ["a3f2e1b4", "b7c4d9a2", ...]

# Query by source type
results = query_by_type("arxiv")
# Returns: ["a3f2e1b4", ...]
```

### Index Management

```python
from lib.storage import rebuild_indexes, get_index_stats

# Rebuild all indexes from metadata.md files
rebuild_indexes()

# Get index statistics
stats = get_index_stats()
# Returns: {
#   'total_content': 42,
#   'total_topics': 15,
#   'topics': ['llm', 'transformers', ...],
#   ...
# }
```

## Hash Collision Handling

Hash collisions are extremely rare with SHA-256, but handled gracefully:

```python
def resolve_hash_collision(full_hash: str, existing_hash: str, current_length: int = 8) -> str:
    # Extend hash prefix until no collision
    for new_length in [12, 16, 20, 32, 64]:
        if new_length <= current_length:
            continue
        new_prefix = full_hash[:new_length]
        existing_prefix = existing_hash[:new_length]
        if new_prefix != existing_prefix:
            return new_prefix
    return full_hash  # Fallback to full hash
```

Collision resolution steps:
1. If `store/a3f2e1b4/` exists but full hash differs
2. Extend to 12 characters: `store/a3f2e1b4c5d6/`
3. If still colliding, extend to 16, then 20, etc.

## Trade-offs

| Aspect | Hash-based | Slug-based Alternative |
|--------|------------|------------------------|
| Uniqueness | Guaranteed (cryptographic) | Requires conflict resolution |
| Human readability | Low | High |
| Deduplication | Automatic (via hash lookup) | Via aggregation or symlinks |
| Collision risk | Negligible | High (semantic conflicts) |
| Discovery tracking | Not built-in | Can track multiple finds |
| Portability | High (plain dirs) | High (plain dirs) |
| LLM-friendly | Via indexes/metadata | Via readable names |

## Format Rationale

- **Markdown + YAML frontmatter**: 15% more token-efficient than JSON for LLMs
- **YAML schemas**: Human-readable, self-documenting
- **JSON indexes**: Fast programmatic access for lookups
- **JSONL sources log**: Append-only, concurrent-safe

# Implementation Status

## Completed

✅ **Hash-based storage architecture** - Directories use 8-character hash prefixes (SHA-256)
✅ **Metadata schema** - Comprehensive YAML frontmatter + markdown body format
✅ **Index system** - by-topic, by-date, by-type, by-hash indexes
✅ **Core storage API** - `store_content()`, `find_content()`, `get_content()`
✅ **Query functions** - Topic, date, and type-based queries
✅ **Progressive disclosure** - Metadata body with Summary, Key Findings, Content Context
✅ **Schema templates** - arXiv papers, tweets, Reddit threads
✅ **Collision handling** - Automatic hash extension on collision

## Future Enhancements

### Vector Search
Reserved fields in metadata schema for future implementation:
- `embeddings`: Vector representation of content
- `embedding_model`: Model used to generate embeddings
- `embedding_timestamp`: When embeddings were generated

Potential approaches:
- Embed full content vs. summary vs. metadata
- Multiple embedding types (semantic, keyword, visual for images)
- Integration with vector databases (Pinecone, Weaviate, etc.)

### Content Enrichment Tools
- CLI/API to iterate through content and enrich metadata bodies
- Integration with MCP model assist for automated annotation
- Manual annotation workflow with progressive refinement
- Extraction of structured data (citations, entities, key claims)

### Discovery Tracking (Optional)
If tracking multiple encounters becomes important:
- Add `found_sources` array to metadata
- Track when/where same content was discovered multiple times
- Aggregate discovery patterns for research insights

### Advanced Querying
- Combined queries (topics AND date range AND type)
- Fuzzy topic matching
- Citation/reference graphs
- Related content suggestions

