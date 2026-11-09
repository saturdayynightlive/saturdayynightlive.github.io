# Design

## Source of truth
Active · 2026-11-09. Surfaces: `index.html`, `projects/simply5x5.html`, shared
`assets/site.css`. Reviewed both pages, existing assets, desktop/mobile renders,
and the Jon Barron and Kai Tzu-iunn Ong academic profiles. This file governs
refinements to the existing static academic layout.

## Brand
Direct, personal, technically grounded. Trust comes from linked affiliations,
released work, and precise dates. Avoid cards, slogans, gradients, decorative
badges, animations, and inflated claims.

## Product goals
Help prospective mentors and collaborators understand the student's interests,
experience, and projects and reach the CV or email quickly. Success means readable
mobile content, clear chronology, working links, and restrained branding.

## Personas and jobs
Research mentors and recruiters scan experience and technical interests.
Collaborators inspect released projects and find contact information.

## Information architecture
`/`: introduction/contact, experience, projects, education, teaching.
`/projects/simply5x5.html`: project description, implementation, release.
Tram project thumbnail links to a figure extracted from the original report.
`/Hwan_Ji_CV.pdf`: text-only CV. Preserve these routes.

## Design principles
Prioritize prose readability over prominent affiliation logos. Portrait and logos
support identification. Keep role, organization, and dates visually distinct.
Allow body copy to occupy the full mobile width, including below the portrait.

## Visual language
White background, near-black text, muted gray metadata, restrained blue links.
Use the existing system sans-serif stack. Body 16px, line height 1.65; section
headings 20px; dates 13px. Content width about 800px. Section spacing 44px,
entry spacing 26px. Thin rules, no shadows. Use original logos and app icon. Profile uses the original studio portrait, with a 10px corner radius and its
natural aspect ratio.

## Components
Shared tokens and typography live in `assets/site.css`. Profile uses a floated
portrait so prose flows beneath it. Affiliation rows use a restrained logo column
on desktop. Mobile places logo and heading together, with prose beneath.
University education uses one SNU logo in the left column. The right column
shows university name, College of Liberal Studies, then Computer Science on
separate lines, without repeated department logos.
Project detail shares type, spacing, links, and focus treatment.

## Accessibility
Target WCAG AA text contrast and keyboard operation. Semantic headings and named
navigation. Visible focus outlines and descriptive image alt text. No motion.
Local image dimensions prevent portrait layout shifts.

## Responsive behavior
Above 600px, use side-by-side headings and dates. At 600px and below, stack dates,
reduce page padding and portrait size, and let entry prose span the content width.
Validate at 360px, 390px, 768px, and 1100px without horizontal scrolling.

## Interaction states
Static pages have no app loading or empty states. Links show hover/focus states.
Core profile and content must remain usable without JavaScript or remote fonts.

## Content voice
First-person, concise, factual. Incoming internship must remain clearly future.
Do not publish internal product names, customer identities, implementation
artifacts, or unsupported metrics. Coursework belongs in the CV. Preserve facts
when editing layout.

## Implementation constraints
Static HTML/CSS, no new dependency or build requirement. Shared CSS changes must
be checked on both routes. Inspect browser screenshots and local links/assets.
PDF layout changes require rendering. Commit only public deliverables.

## Open questions
No blocking questions. Safari and Firefox remain outside this refinement's
browser verification scope.
