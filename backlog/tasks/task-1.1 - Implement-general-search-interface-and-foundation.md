---
id: task-1.1
title: Implement general search interface and foundation
status: Done
assignee: []
created_date: '2025-11-26 01:22'
updated_date: '2025-11-26 01:53'
labels:
  - skill
  - research
  - foundation
dependencies: []
parent_task_id: task-1
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the foundational search interface that all source-specific implementations will extend. This defines the common parameters (topic, time-bounds, sources) and the expected output format (content storage following doc-03).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Define shared search parameters: topic query, time-bounds (start/end dates), source filters
- [x] #2 Implement content storage interface following doc-03: slugified directories, meta.md with YAML frontmatter, content files
- [x] #3 Implement deduplication logic using content hashing and hash index
- [x] #4 Create ingestion function that handles both new content and aggregation of duplicate findings
- [x] #5 Define base schema for metadata (title, type, content_hash, found_sources, topics)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Define search parameter interface\n2. Implement storage utilities (slug generation, directory creation)\n3. Implement hash-based deduplication\n4. Create ingestion pipeline\n5. Set up index management (by-hash.json)
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Complete

Implemented all foundational components in `src/reflow/lib/research/`:

### Created Modules

1. **models.py** - Data models and interfaces
   - SearchParams: topic, time-bounds, source filters
   - ContentMetadata: comprehensive metadata schema
   - FoundSource: discovery history tracking
   - ContentType & SourceType enums

2. **storage.py** - Storage utilities
   - Slugification with unicode normalization
   - Conflict resolution (year, author, numeric)
   - Directory management
   - YAML frontmatter read/write
   - Content file handling

3. **deduplication.py** - Hash-based deduplication
   - SHA-256 content hashing
   - Hash index management (by-hash.json)
   - Duplicate detection
   - Aggregation logic for duplicate content

4. **ingestion.py** - Main ingestion pipeline
   - `ingest_content()` - full pipeline
   - `bulk_ingest()` - batch processing
   - IngestionResult for feedback
   - Automatic deduplication handling

5. **indexing.py** - Derived index management
   - Topic index (by-topic.json)
   - Type index (by-type.json)
   - Date index (by-date.json)
   - Index rebuild capabilities
   - Query methods for each index

### Documentation

- Comprehensive README.md with usage examples
- requirements.txt for dependencies (PyYAML)

### Storage Architecture

Follows doc-03 specification:
- Slugified directories with semantic names
- meta.md with YAML frontmatter
- Content files with appropriate extensions
- Hash-based deduplication via by-hash.json
- Derived indexes that can be rebuilt

All acceptance criteria met. Ready for source-specific implementations (arXiv, Twitter, etc.)
<!-- SECTION:NOTES:END -->
