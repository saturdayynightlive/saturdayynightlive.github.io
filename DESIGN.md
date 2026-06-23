# Design

## Source of truth
- Status: Active
- Last refreshed: 2026-06-24
- Primary product surfaces: Root personal homepage at `index.html`; project detail pages under `projects/`
- Evidence reviewed: `index.html`, `projects/simply5x5.html`, `Hwan_Ji_CV.pdf`, `DESIGN.md`, LaTeX.css documentation at `https://latex.vercel.app/`

## Brand
- Personality: Academic, plain, precise, and document-like.
- Trust signals: CV link, university affiliation, project evidence, course plan, contact links, and App Store release links where relevant.
- Avoid: Decorative operating-system chrome, fake counters, loud retro widgets, marketing-page composition, and heavy card layouts.

## Product goals
- Goals: Present Hwan Ji as a Computer Science & Engineering undergraduate with interests in data-centered AI, statistics, and practical software systems.
- Non-goals: Simulate a full application shell, add backend features, or rely on paid/external APIs.
- Success signals: The page reads like a concise academic profile, keeps prose minimal, and remains easy to scan on mobile.

## Personas and jobs
- Primary personas: Peers, professors, research mentors, recruiters, and collaborators.
- User jobs: Confirm identity and affiliation, inspect interests/projects/CV, open representative project details, find contact information, and review coursework.
- Key contexts of use: Mobile and desktop browsers through GitHub Pages.

## Information architecture
- Primary navigation: About, Projects, Coursework, Contact.
- Core routes/screens: Static root page, representative project detail pages, and linked PDF CV.
- Content hierarchy: Title and author block, short fact list with portrait, unnumbered sections, representative projects, and compact coursework table.

## Design principles
- Principle 1: Prefer semantic HTML that LaTeX.css can typeset with minimal custom classes.
- Principle 2: Keep the page closer to a paper handout than a dashboard.
- Principle 3: Keep the homepage lighter than the CV; detailed honors, teaching, and full credentials belong in the PDF.
- Principle 4: Prefer factual labels, lists, and tables over explanatory prose.
- Tradeoffs: Less playful than the DOS98 experiment, but better aligned with a durable academic personal site.

## Visual language
- Color: Mostly LaTeX.css defaults; use black text, white paper, and restrained rules.
- Typography: LaTeX.css Latin Modern defaults; avoid custom webfont stacks unless readability requires it.
- Spacing/layout rhythm: Narrow article measure, unnumbered sections, compact tables, simple lists.
- Shape/radius/elevation: No rounded cards, no shadows, no synthetic depth.
- Motion: None.
- Imagery/iconography: Use the profile photo as the primary share image; keep browser chrome unbranded.

## Components
- Existing components to reuse: LaTeX.css `author`, standard document typography, and table utility classes.
- Components to avoid: LaTeX.css theorem/proof/definition boxes unless the page later contains actual mathematical or technical notes that need them.
- New/changed components: Small local helpers for navigation, profile figure, project metadata, responsive tables, and share-preview metadata.
- Variants and states: Links use browser/LaTeX.css defaults; no JavaScript states.
- Token/component ownership: LaTeX.css owns global document typography and base element styles. `index.html` owns small page-specific layout helpers.

## Accessibility
- Target standard: Static semantic HTML with accessible links, headings, image alt text, and responsive behavior.
- Keyboard/focus behavior: Native link and browser focus behavior.
- Contrast/readability: Use LaTeX.css defaults and avoid low-contrast decorative colors.
- Screen-reader semantics: Preserve heading order, table headers, `nav` label, figure alt/caption, and meaningful link text.
- Reduced motion and sensory considerations: No animation or smooth scrolling.

## Responsive behavior
- Supported breakpoints/devices: Mobile phones, tablets, and desktop browsers.
- Layout adaptations: Profile image stops floating on small screens; wide tables can scroll horizontally.
- Touch/hover differences: No hover-dependent content.

## Interaction states
- Loading: Static HTML and CSS only.
- Empty: Not applicable.
- Error: If the external stylesheet fails, semantic HTML remains readable.
- Success: Root and project pages load with LaTeX.css styling and the core public-profile/project content visible.
- Disabled: Not applicable.
- Offline/slow network: Core content remains readable without JavaScript; external CSS may load later.

## Content voice
- Tone: Concise, academic, and factual.
- Terminology: Use concrete roles, project evidence, and course names.
- Microcopy rules: Avoid joke UI text, fake system labels, visual instructions, and generic explanatory paragraphs.

## Implementation constraints
- Framework/styling system: Single static `index.html` on GitHub Pages using LaTeX.css from `https://latex.vercel.app/style.css`.
- Design-token constraints: Keep custom CSS narrow and page-specific.
- Performance constraints: No build step, no JavaScript, no backend.
- Compatibility constraints: Must work as a static GitHub Pages root page.
- Test/screenshot expectations: Verify CSS request success, no console errors, no mobile horizontal overflow, valid internal links, and core profile/project sections remain present.

## Open questions
- [ ] Decide whether to pin LaTeX.css to a vendored local copy for offline durability.
