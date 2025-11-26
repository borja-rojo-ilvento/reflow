---
id: task-1.2
title: Implement arXiv source integration
status: To Do
assignee: []
created_date: '2025-11-26 01:22'
labels:
  - skill
  - research
  - arxiv
  - integration
dependencies:
  - task-1.1
parent_task_id: task-1
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement arXiv-specific search functionality using the general search interface. Uses progressive disclosure to expose arXiv-specific parameters (categories, authors, IDs) while maintaining the common interface for topic and time-based searches.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Integrate with arXiv API for paper searches
- [ ] #2 Support arXiv-specific parameters via progressive disclosure: categories, author search, arXiv ID lookup
- [ ] #3 Extract and store paper metadata: title, authors, abstract, categories, publication date
- [ ] #4 Download and store PDF content as content.pdf
- [ ] #5 Generate proper slugs from paper titles
- [ ] #6 Handle arXiv-specific metadata fields in meta.md frontmatter
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Implement arXiv API client\n2. Create parameter interface extending base search params\n3. Implement progressive disclosure for arXiv-specific filters\n4. Add PDF download and storage\n5. Map arXiv metadata to storage schema\n6. Test with various query types (topic, author, category, ID)
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
arXiv API: http://export.arxiv.org/api/query - Use RSS/Atom feed format for results. Consider rate limiting and batch downloads.
<!-- SECTION:NOTES:END -->
