# Design

## Source of truth
- Status: Active
- Last refreshed: 2026-06-14
- Primary product surfaces: Root personal homepage at `index.html`
- Evidence reviewed: `index.html`, `Hwan_Ji_CV.pdf`, `DESIGN.md`, Lab12 GitHub Pages requirements, LaTeX.css documentation at `https://latex.vercel.app/`

## Brand
- Personality: Academic, plain, precise, and document-like.
- Trust signals: CV download, university affiliation, project evidence, course plan, contact links.
- Avoid: Decorative operating-system chrome, fake counters, loud retro widgets, marketing-page composition, and heavy card layouts.

## Product goals
- Goals: Present Hwan Ji as a Computer Science & Engineering undergraduate with interests in data-centered AI, statistics, and practical software systems.
- Non-goals: Simulate a full application shell, add backend features, or rely on paid/external APIs.
- Success signals: The page reads like a concise academic profile, satisfies Lab12 required content, and remains easy to scan on mobile.

## Personas and jobs
- Primary personas: Teaching assistants checking Lab12, peers, professors, research mentors, and collaborators.
- User jobs: Confirm identity and affiliation, inspect interests/projects/CV, find contact information, and review planned courses.
- Key contexts of use: Mobile and desktop browsers through GitHub Pages.

## Information architecture
- Primary navigation: Abstract, About, Currently, Projects, Resume, Courses, Contact, AI Usage.
- Core routes/screens: Single static root page plus linked PDF CV.
- Content hierarchy: Title and author block, abstract with portrait, numbered sections, ordinary prose, and tables for resume/course summaries.

## Design principles
- Principle 1: Prefer semantic HTML that LaTeX.css can typeset with minimal custom classes.
- Principle 2: Keep the page closer to a paper handout than a dashboard.
- Tradeoffs: Less playful than the DOS98 experiment, but better aligned with a durable academic personal site.

## Visual language
- Color: Mostly LaTeX.css defaults; use black text, white paper, and restrained rules.
- Typography: LaTeX.css Latin Modern defaults; avoid custom webfont stacks unless readability requires it.
- Spacing/layout rhythm: Narrow article measure, numbered sections, compact tables, simple lists.
- Shape/radius/elevation: No rounded cards, no shadows, no synthetic depth.
- Motion: None.
- Imagery/iconography: Use the profile photo as the only primary visual asset.

## Components
- Existing components to reuse: LaTeX.css `author`, `abstract`, standard document typography, and table utility classes.
- Components to avoid: LaTeX.css theorem/proof/definition boxes unless the page later contains actual mathematical or technical notes that need them.
- New/changed components: Small local helpers for navigation, profile figure, project metadata, and responsive tables.
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
- Success: Page loads with LaTeX.css styling and all required Lab12 content visible.
- Disabled: Not applicable.
- Offline/slow network: Core content remains readable without JavaScript; external CSS may load later.

## Content voice
- Tone: Concise, academic, first-person where appropriate.
- Terminology: Use concrete roles, project evidence, and course names.
- Microcopy rules: Avoid joke UI text, fake system labels, and visual instructions inside the app.

## Implementation constraints
- Framework/styling system: Single static `index.html` on GitHub Pages using LaTeX.css from `https://latex.vercel.app/style.css`.
- Design-token constraints: Keep custom CSS narrow and page-specific.
- Performance constraints: No build step, no JavaScript, no backend.
- Compatibility constraints: Must work as a static GitHub Pages root page.
- Test/screenshot expectations: Verify CSS request success, no console errors, no mobile horizontal overflow, and Lab12 required sections remain present.

## Open questions
- [ ] Decide whether to pin LaTeX.css to a vendored local copy for offline durability.
