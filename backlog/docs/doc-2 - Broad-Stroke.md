---
id: doc-2
title: Broad Stroke
type: other
created_date: '2025-11-21 02:39'
---
Extract: Information Sources & Methods

Source Types & Characteristics

Web Sources:
- Academic papers (arXiv, papers with code): Structured, high-quality, requires PDF/LaTeX parsing
- News sites & blogs: Semi-structured HTML, varying quality, requires content extraction from boilerplate
- Social media (Twitter/X, Reddit, HN): Real-time, conversational, requires thread/context aggregation
- Documentation sites: Technical, structured, often has navigation hierarchies
- RSS feeds: Pre-structured, standardized format (XML/Atom)
- YouTube transcripts: Time-coded, conversational, requires summarization

Extraction Methods:
- Web scraping (BeautifulSoup, Playwright): Full control, fragile to changes
- APIs: Reliable, rate-limited, requires authentication
- RSS/Atom feeds: Standardized, often incomplete content
- Browser automation: Handles JavaScript, resource-intensive
- Content extraction libraries (Readability, Trafilatura): Removes boilerplate, works across sites

Storage Architecture Considerations

Let me explore different approaches:

Simple Approaches:
research/
├── raw/                    # Original extracted content
│   ├── web/
│   │   ├── YYYY-MM-DD_source_hash.html
│   │   └── YYYY-MM-DD_source_hash.json
│   ├── papers/
│   │   └── arxiv_2024_12345.pdf
│   └── social/
│       └── twitter_thread_abc123.json
├── processed/              # Cleaned/transformed
└── metadata/               # Indexes, tags, relationships
  └── sources.json

Graph-Based Approach:
research/
├── nodes/                  # Individual pieces of information
│   ├── n001_concept.md
│   ├── n002_paper.md
│   └── n003_quote.md
├── edges/                  # Relationships between nodes
│   └── relationships.json
└── views/                  # Different aggregations
  ├── by-topic/
  └── by-date/

Database-Like Approach:
research/
├── content/
│   └── [hash-based storage]
├── index/
│   ├── full-text.idx
│   ├── tags.idx
│   └── sources.idx
└── schemas/
  └── content-types.json

Hybrid File System:
research/
├── sources/                # One folder per source
│   ├── arxiv/
│   │   ├── raw/
│   │   ├── extracted/
│   │   └── metadata.json
│   └── twitter/
├── topics/                 # Cross-referenced views
│   ├── llm-reasoning/
│   │   ├── links.json     # References to sources
│   │   └── summary.md
└── pipeline/
  ├── extraction/
  ├── transformation/
  └── loading/

Format Considerations by Data Type

| Data Type | Best Storage                 | Retrieval Method         | Transformation Ease       |
|-----------|------------------------------|--------------------------|---------------------------|
| Articles  | Markdown + YAML frontmatter  | grep, full-text search   | High - text processing    |
| Papers    | PDF + extracted.md           | Vector embeddings        | Medium - needs parsing    |
| Tweets    | JSON with thread context     | Structured query         | High - already structured |
| Videos    | JSON (transcript + metadata) | Time-coded search        | Medium - needs chunking   |
| Images    | Original + OCR text          | Visual similarity + text | Low - needs ML models     |
| Code      | Original + AST               | Semantic search          | High - parseable          |

● Storage Mechanisms Deep Dive

Recommended: Content-Addressable + Metadata Layer

This approach balances flexibility with maintainability:

.research/                          # Hidden to avoid clutter
├── config.json                     # Pipeline configuration
├── store/                          # Content-addressable storage
│   ├── content/
│   │   ├── a3f2e1b.md             # Hash-based filenames
│   │   ├── b7c4d9a.json
│   │   └── c1e5f2d.pdf
│   └── cache/                      # Temporary processing
├── meta/                           # Rich metadata layer
│   ├── sources.jsonl               # One source per line (append-only)
│   ├── tags.json                   # Tag index
│   ├── graph.json                  # Relationship graph
│   └── timeline.json               # Temporal index
└── queries/                        # Saved searches/views
  └── llm-reasoning.query.json

research/                           # Human-readable workspace
├── drafts/                         # Newsletter drafts
├── topics/                         # Curated topic collections
│   └── [topic-name]/
│       ├── README.md               # Overview
│       ├── sources.md              # Annotated link list
│       └── notes.md                # Synthesis notes
└── archive/
  └── 2025-W47/                   # Weekly archives

Why This Works:

1. Content-addressable storage prevents duplication and enables deduplication
2. JSONL for sources allows append-only writes (safe for concurrent access)
3. Separate metadata enables multiple views without duplicating content
4. Human-readable workspace for actual writing and curation
5. Git-friendly - text-based formats, logical structure

● Transform: Data Manipulation Patterns

Transformation Pipeline Stages

Stage 1: Normalization
- HTML → Markdown (Pandoc, Turndown)
- PDF → Text (pdftotext, PyPDF2)
- Video → Transcript (Whisper, YouTube API)
- Cleaning (remove ads, boilerplate, formatting artifacts)

Stage 2: Enrichment
- Entity extraction (authors, organizations, dates)
- Topic classification/tagging
- Sentiment analysis
- Link resolution and archival
- Citation extraction

Stage 3: Synthesis (LLM-powered)
- Summarization (multiple lengths: tweet, paragraph, detailed)
- Key point extraction
- Question generation ("What does this enable?")
- Relationship identification
- Quality scoring

Stage 4: Structuring
- Converting to common schema
- Adding metadata (source credibility, publication date, relevance score)
- Creating bidirectional links
- Building knowledge graph edges

Transformation Tooling Strategy

Declarative Transform Definitions:
{
"transforms": {
  "web-article": {
    "pipeline": [
      {"step": "fetch", "method": "http"},
      {"step": "extract", "tool": "trafilatura"},
      {"step": "convert", "to": "markdown"},
      {"step": "llm-summarize", "lengths": ["short", "medium"]},
      {"step": "tag", "taxonomy": "topics.json"},
      {"step": "store", "format": "content-addressed"}
    ]
  },
  "arxiv-paper": {
    "pipeline": [
      {"step": "fetch", "source": "arxiv-api"},
      {"step": "extract-pdf-text"},
      {"step": "extract-sections"},
      {"step": "llm-extract", "targets": ["methodology", "results", "implications"]},
      {"step": "store"}
    ]
  }
}
}

Composable Transform Functions:
# Transforms as pure functions
def normalize_html(content: str) -> str:
  """HTML → clean markdown"""

def extract_entities(text: str) -> List[Entity]:
  """Text → structured entities"""

def llm_summarize(text: str, length: str) -> str:
  """Text → summary (via Claude)"""

def build_graph_edges(doc: Document) -> List[Edge]:
  """Document → relationships"""

# Compose into pipelines
pipeline = (
  fetch_url
  | normalize_html
  | extract_entities
  | llm_summarize("short")
  | store_content
)

LLM-Powered Transformations

Claude Code can perform rich transformations:

1. Smart Summarization: Context-aware, preserving technical nuance
2. Cross-referencing: "This relates to paper X because..."
3. Insight Extraction: "The key insight is..."
4. Quality Assessment: Credibility scoring, bias detection
5. Format Conversion: Technical → accessible language
6. Deduplication: Semantic similarity detection

Data Format Standards

Source Document Schema:
{
"id": "sha256-hash",
"type": "web-article",
"source": {
  "url": "https://...",
  "fetched_at": "2025-11-20T10:00:00Z",
  "title": "...",
  "author": "...",
  "published_at": "2025-11-15T00:00:00Z"
},
"content": {
  "raw": "content/a3f2e1b.html",
  "markdown": "content/a3f2e1b.md",
  "summary_short": "...",
  "summary_medium": "..."
},
"metadata": {
  "tags": ["llm", "reasoning", "research"],
  "entities": [...],
  "quality_score": 0.87,
  "reading_time_minutes": 12
},
"relationships": {
  "cited_by": [],
  "cites": [],
  "related_to": []
}
}

● Load: Retrieval & Usability Strategies

Query Interface Design

Multi-Modal Retrieval:
# Temporal queries
research query --last-week
research query --date-range 2025-11-01 2025-11-15

# Topic-based
research query --tag llm --tag reasoning
research query --topic "multimodal AI"

# Quality filtering
research query --min-quality 0.8 --type paper

# Hybrid semantic search
research search "how do LLMs handle long context?"

# Graph traversal
research related <document-id> --depth 2
research citations <document-id> --recursive

View Generation for Newsletter Writing

Pre-computed Views:
research/views/
├── this-week.md              # Auto-generated weekly digest
├── trending.md               # Most-linked/cited content
├── deep-dives/               # Curated long-form
│   └── [topic].md
└── quick-hits/               # Short noteworthy items

Dynamic View Example (this-week.md):
# Research Digest: Week of 2025-11-18

## Major Developments (3)
- [Title](link) - Quality: ⭐⭐⭐⭐⭐
> Key insight in 1-2 sentences
> Why it matters...

## Papers (5)
### Reasoning & Planning
- [Paper Title](arxiv) - Smith et al.
**TL;DR**: One sentence summary
**Key Finding**: Main result
**Implications**: Why newsletter readers care

## Noteworthy Threads (8)
- [@username](link): "Quote..."
💡 Insight extraction...

## Patterns & Themes
This week showed convergence around [theme]...

---
Generated: 2025-11-20 | Sources: 47 | Quality filter: >0.7

Integration with Writing Workflow

Newsletter Draft Assistance:
# Start new newsletter
research newsletter create --week 2025-W47

# Generate sections
research newsletter section "major-developments" --limit 3
research newsletter section "paper-roundup" --tag papers

# Get context for writing
research expand <source-id>  # Full details for deep-dive
research quote <source-id>   # Get quotable excerpts
research check-duplicates    # Avoid repeating past content

Claude Code Plugin Integration:
Slash commands in Claude Code:
- /research-query [query] - Search research database
- /research-summarize [url] - Fetch and summarize new content
- /research-add [url] - Add to research pipeline
- /newsletter-draft - Generate draft from week's research
- /newsletter-expand [section] - Elaborate on a section

Data Cleanliness & Usability

Clean Data Characteristics:
1. Consistent schema - All sources normalized to common format
2. Quality scored - Filterable by credibility/relevance
3. Deduplicated - Same story from multiple sources merged
4. Timestamped - Clear provenance and freshness
5. Summarized - Multiple abstraction levels available
6. Linked - Relationships explicit and traversable
7. Tagged - Multiple classification systems
8. Annotated - Context and relevance notes

Fetchable Data Requirements:
- Fast text search (ripgrep, SQLite FTS5)
- Structured queries (JSON/SQL-like)
- Vector similarity (embeddings for semantic search)
- Graph queries (relationships and citations)
- Temporal indexing (by publication/fetch date)

MCP Resource Exposure

As a Claude Code plugin, expose via MCP:
{
"resources": {
  "research://digest/weekly": "This week's research summary",
  "research://digest/monthly": "This month's themes",
  "research://query/{query}": "Search research database",
  "research://topic/{topic}": "All content for topic",
  "research://source/{id}": "Full source details"
}
}

● Synthesized Plugin Architecture Proposal

Recommended Approach: Hybrid File-Based System with MCP Integration

Core Principles:
1. Git-friendly - Text files, logical structure, meaningful diffs
2. Claude-first - Optimized for LLM reading and writing
3. Human-readable - Markdown and JSON for manual curation
4. Incremental - Start simple, add complexity as needed
5. Composable - Modular pipeline stages

Proposed File Structure

your-project/
├── .research/                      # Plugin workspace (gitignored binaries)
│   ├── config.yaml                 # Pipeline configuration
│   ├── store/
│   │   ├── content/                # Content-addressed storage
│   │   │   ├── [hash].md
│   │   │   ├── [hash].json
│   │   │   └── [hash].pdf
│   │   └── embeddings/             # Vector embeddings cache
│   │       └── vectors.db
│   ├── meta/
│   │   ├── sources.jsonl           # Append-only source log
│   │   ├── tags.json               # Tag taxonomy and index
│   │   ├── graph.json              # Relationship graph
│   │   └── quality.json            # Quality scores and notes
│   ├── transforms/
│   │   ├── pipelines/              # Transform pipeline definitions
│   │   └── cache/                  # Intermediate processing results
│   └── indexes/
│       ├── fulltext.db             # SQLite FTS5 for text search
│       ├── timeline.json           # Temporal index
│       └── topics.json             # Topic clustering
│
├── research/                       # Human-readable workspace (git-tracked)
│   ├── sources/                    # Curated source collections
│   │   ├── papers.md
│   │   ├── articles.md
│   │   └── threads.md
│   ├── topics/
│   │   └── [topic-name]/
│   │       ├── overview.md
│   │       ├── sources.md
│   │       └── notes.md
│   ├── weekly/
│   │   └── 2025-W47/
│   │       ├── digest.md           # Auto-generated
│   │       ├── newsletter.md       # Draft
│   │       └── archive.md          # Published version
│   └── templates/
│       ├── newsletter.md
│       └── deep-dive.md
│
└── .claude/
  └── commands/
      ├── research-add.md         # /research-add [url]
      ├── research-query.md       # /research-query [query]
      ├── newsletter-draft.md     # /newsletter-draft
      └── research-config.md      # /research-config

Technology Stack Recommendation

Phase 1: MVP (Minimal Viable Plugin)
- Storage: Files (markdown + JSON)
- Search: ripgrep for text, jq for JSON
- Extraction: Python + Trafilatura + Requests
- Transform: Claude API for summarization
- Interface: Claude Code slash commands

Phase 2: Enhanced
- Search: SQLite FTS5 for full-text
- Embeddings: Local embedding model for semantic search
- Graph: NetworkX for relationship queries
- Pipeline: Declarative YAML-based transforms

Phase 3: Advanced
- Real-time: Watch feeds, auto-extract
- Collaboration: Shared research workspaces
- Intelligence: Auto-tagging, duplicate detection
- Analytics: Trend detection, topic evolution

Implementation Phases

Phase 1: Foundation (Week 1-2)
✓ Basic file structure
✓ Simple extraction (RSS, web scraping)
✓ Storage (markdown files with YAML frontmatter)
✓ One slash command: /research-add [url]
✓ Manual curation workflow

Phase 2: Automation (Week 3-4)
✓ Automatic summarization pipeline
✓ Quality scoring
✓ Search and query interface
✓ Weekly digest generation
✓ /newsletter-draft command

Phase 3: Intelligence (Week 5-6)
✓ Semantic search
✓ Topic clustering
✓ Relationship detection
✓ Trend analysis
✓ Duplicate detection

Concrete Example: Newsletter Workflow

Monday: Collection
/research-add https://arxiv.org/abs/2025.12345
/research-add https://blog.example.com/new-llm-technique
# Plugin automatically:
# 1. Fetches content
# 2. Extracts text
# 3. Generates summaries (short, medium, detailed)
# 4. Tags with topics
# 5. Scores quality
# 6. Stores in .research/store/
# 7. Updates indexes

Wednesday: Review
/research-query --this-week --min-quality 0.8
# Returns markdown list of high-quality sources from this week
# Claude helps you curate and annotate

Friday: Draft
/newsletter-draft
# Generates research/weekly/2025-W47/newsletter.md with:
# - Categorized sources
# - AI-written summaries
# - Suggested sections
# - Thematic analysis

# You then edit and refine with Claude's help

Key Design Decisions & Trade-offs

| Decision                       | Rationale                              | Trade-off                      |
|--------------------------------|----------------------------------------|--------------------------------|
| Files over database            | Git-friendly, human-readable, portable | Slower queries at scale        |
| Content-addressed storage      | Deduplication, immutability            | Harder to browse manually      |
| JSONL for append-only logs     | Concurrent-safe, simple                | No random updates              |
| Markdown with YAML frontmatter | LLM-friendly, editable, standard       | Less structured than pure JSON |
| SQLite for search (Phase 2)    | Embedded, powerful, standard           | Adds dependency                |
| Local-first                    | Privacy, offline, fast                 | No automatic sync              |

MCP Server Interface

# .research/config.yaml
mcp:
server_name: research
version: 1.0.0

resources:
  - uri: research://digest/weekly
    name: "Weekly Research Digest"
    mime_type: text/markdown

  - uri: research://digest/monthly
    name: "Monthly Research Digest"
    mime_type: text/markdown

  - uri: research://query/{query}
    name: "Search Research Database"
    mime_type: application/json

  - uri: research://topic/{topic}
    name: "Topic Collection"
    mime_type: text/markdown

tools:
  - name: research_add
    description: "Add a source to the research database"
    parameters:
      url: string
      tags: string[]?
      priority: number?

  - name: research_query
    description: "Query the research database"
    parameters:
      query: string
      filters: object?

  - name: newsletter_generate
    description: "Generate newsletter draft from research"
    parameters:
      week: string
      template: string?

Getting Started: Minimal First Steps

1. Create basic structure (5 min)
2. Write simple Python extraction script (30 min)
3. Create /research-add slash command (15 min)
4. Test with 5-10 sources (30 min)
5. Manually draft newsletter to validate data (1 hour)
6. Iterate based on friction points

● ---
Summary

I've explored a comprehensive ETL architecture for a research aggregation plugin for Claude Code. Here are the key findings:

Core Recommendation

Hybrid file-based system with:
- Content-addressable storage for deduplication
- Human-readable markdown workspace for curation
- Incremental complexity (start simple, add features)
- MCP integration for Claude Code access

Critical Success Factors

1. Start minimal - Files, basic extraction, one slash command
2. Make it Claude-friendly - Markdown, clear structure, rich metadata
3. Git-trackable - Version control for research and newsletters
4. Composable transformations - Build pipeline incrementally
5. Human-in-loop - Auto-generate, human curate

Next Steps Options

Would you like me to:
1. Implement Phase 1 MVP - Create the basic file structure, extraction script, and first slash command?
2. Deep-dive a specific area - Detailed implementation of extraction, transformation, or loading?
3. Create alternative architectures - Database-centric or graph-first approaches?
4. Build a prototype - Working example with real sources to test the concept?

The architecture is designed to grow with your needs - starting with simple file-based storage and manual curation, then adding
automation, search, and intelligence as patterns emerge from actual use.

