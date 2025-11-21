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
├── breakthrough-in-chain-of-thought/
│   ├── meta.md
│   └── content.html
│
├── empirical-scaling-laws/
│   ├── meta.md
│   └── content.pdf
│
├── karpathy-scaling-lecture/
│   ├── meta.md
│   ├── content.mp4
│   └── transcript.md

schemas/
├── article.schema.yaml
├── paper.schema.yaml
└── video.schema.yaml

indexes/
├── by-topic.json
├── by-type.json
├── by-date.json
└── by-hash.json

sources.jsonl
```

## Design Principles

- **Flat structure**: Minimize hierarchy to maintain flexibility
- **Semantic naming**: Directory names are human/LLM-readable slugs
- **Differentiation by inspection**: Metadata describes content type, not file paths
- **Schema-driven**: Self-describing type definitions in `schemas/`
- **Indexes are derived**: Can be rebuilt from `meta.md` files

## Key Components

### Store Directories

Each piece of content is a directory containing:
- `meta.md`: YAML frontmatter + markdown notes
- `content.{ext}`: Original content file (html, pdf, mp4, etc.)
- Additional files as needed (e.g., `transcript.md` for videos)

### Hash Index (`indexes/by-hash.json`)

Maps content hash to slug for deduplication:

```json
{
  "a3f2e1b4c5d6e7f8...": "breakthrough-in-chain-of-thought",
  "b7c4d9a2e3f1g8h9...": "empirical-scaling-laws"
}
```

### Metadata Format (`meta.md`)

```markdown
---
type: article
title: "Breakthrough in Chain-of-Thought Reasoning"
content_hash: a3f2e1b4c5d6e7f8...
content_file: content.html

# Discovery history
first_found: 2025-11-15T08:00:00Z
last_found: 2025-11-20T14:30:00Z
found_count: 3
found_sources:
  - url: https://arxiv.org/abs/2025.12345
    at: 2025-11-15T08:00:00Z
  - url: https://news.ycombinator.com/item?id=123456
    at: 2025-11-18T10:00:00Z
  - url: https://twitter.com/researcher/status/789
    at: 2025-11-20T14:30:00Z

topics:
  - llm
  - reasoning
---

# Summary
...
```

## Deduplication via Aggregation

When content is encountered again:
1. Compute content hash
2. Look up in `indexes/by-hash.json`
3. If found: update existing `meta.md` with new `found_sources` entry, increment `found_count`, update `last_found`
4. If not found: create new directory with slug

## Ingestion Logic

```python
def ingest(url: str, content: bytes, metadata: dict):
    content_hash = sha256(content)

    # Check if we've seen this content before
    hash_index = load_json("indexes/by-hash.json")

    if content_hash in hash_index:
        # AGGREGATION: Update existing entry
        slug = hash_index[content_hash]
        meta_path = f"store/{slug}/meta.md"
        meta = frontmatter.load(meta_path)

        meta['last_found'] = now()
        meta['found_count'] = meta.get('found_count', 1) + 1
        meta['found_sources'].append({
            'url': url,
            'at': now()
        })

        frontmatter.dump(meta, meta_path)
        return slug  # No new storage needed

    else:
        # NEW: Create entry
        slug = slugify(metadata['title'])
        slug = resolve_conflicts(slug)

        dir_path = f"store/{slug}"
        mkdir(dir_path)

        write_file(f"{dir_path}/content.{ext}", content)
        write_meta(f"{dir_path}/meta.md", {
            **metadata,
            'content_hash': content_hash,
            'first_found': now(),
            'last_found': now(),
            'found_count': 1,
            'found_sources': [{'url': url, 'at': now()}]
        })

        # Update hash index
        hash_index[content_hash] = slug
        save_json("indexes/by-hash.json", hash_index)

        return slug
```

## Slug Generation

```python
def slugify(text: str, max_length: int = 60) -> str:
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
```

## Conflict Resolution

If slug already exists:
1. Append year if available: `attention-is-all-you-need-2017`
2. Append author if available: `attention-is-all-you-need-vaswani`
3. Append numeric suffix: `attention-is-all-you-need-2`

## Trade-offs

| Aspect | This Design | Alternative (Git-style) |
|--------|-------------|-------------------------|
| Simplicity | High | Medium |
| LLM-friendly | Yes | Yes (via workspace/) |
| Deduplication | Via aggregation | Via content-addressing |
| Multiple views | Via indexes | Via symlinks |
| Portability | High (plain dirs) | Medium (symlinks) |

## Format Rationale

- **Markdown + YAML frontmatter**: 15% more token-efficient than JSON for LLMs
- **YAML schemas**: Human-readable, self-documenting
- **JSON indexes**: Fast programmatic access for lookups
- **JSONL sources log**: Append-only, concurrent-safe
