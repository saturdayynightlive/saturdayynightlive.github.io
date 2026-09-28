# Design

Updated: 2026-09-28

## Scope
The personal homepage and Simply5x5 project page use a conventional academic
profile layout. Study notes under docs/ keep their own document layouts.

## Content
- Name, SNU affiliation, short ML/AI interests, and contact/CV links.
- Current internship and teaching experience.
- Selected projects with concise, factual descriptions.
- Coursework belongs in the CV, separated into completed and in progress.
- Do not publish course assignment solutions, internal internship documents,
  private archives, personal identifiers, or unsupported performance claims.
- RAG is a prototype, not a deployed product. Do not equate retrieval evidence
  coverage with answer accuracy.

## Layout
White background, restrained blue links, system sans-serif typography.
A narrow centered column with a small existing portrait in the introduction.
Experience and project entries use headings, dates, and plain paragraphs.
No cards, hero slogans, gradients, animation, or lengthy personal manifesto.
On phones dates stack below titles; links wrap naturally.

## Implementation
index.html and projects/simply5x5.html share assets/site.css.
Static HTML/CSS, no build or JavaScript dependency. Preserve existing URLs.
CV source is Hwan_Ji_CV.tex; rebuild Hwan_Ji_CV.pdf after content changes.
Do not compress the CV just to hit a page count.

## Verification
Check desktop and mobile layouts, keyboard focus, local link targets, image
loading, and PDF page breaks. Commit only public deliverables.
