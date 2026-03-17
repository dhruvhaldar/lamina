## 2026-03-05 - Destroying Accessibility Hints via innerText
**Learning:** Overwriting a button's `innerText` (e.g., during loading states) destroys internal HTML elements like spans used for keyboard hints (`<span class="shortcut-hint" aria-hidden="true">`), permanently breaking visual UX and accessibility features after a single interaction.
**Action:** Always store and restore `innerHTML` (or use CSS pseudo-elements/hidden spans) when manipulating button states to preserve internal DOM structure and ARIA attributes.

## 2026-03-05 - Making Dynamic Inline Validation Accessible
**Learning:** Visual-only inline validation errors (e.g., turning text red and updating a sibling `div` with an error message) are invisible to screen readers unless explicitly linked.
**Action:** When creating dynamic error message containers, add `aria-live="polite"` and dynamically link the container's ID to the input's `aria-describedby` attribute to ensure AT users are informed of validation failures as they type.

## 2026-03-07 - Empty State Visual Polish
**Learning:** Text-only empty states can appear unpolished to users and fail to convey the type of content expected in that area.
**Action:** Always include a decorative SVG icon (with `aria-hidden="true"` and `focusable="false"`) alongside helper text in empty states to provide visual structure and clarity.

## 2026-03-08 - Semantic Landmarks for Form Grouping
**Learning:** Using generic `<div>` containers for major form sections provides no structural context for Assistive Technologies. Screen reader users benefit immensely from explicit document landmarks.
**Action:** Always convert primary UI panels to semantic `<section>` elements and explicitly link them to their visible headings using `aria-labelledby`.

## 2026-03-08 - Redundant ARIA Labels on Explicitly Labeled Fields
**Learning:** Applying an `aria-label` to an input element that already has an explicitly associated `<label for="...">` causes screen readers to announce the label twice, creating auditory clutter.
**Action:** Avoid redundant `aria-label` attributes on form controls if an accessible `<label>` is already properly linked.

## 2026-03-20 - Semantic Abbreviations for Discoverability
**Learning:** Using `title` attributes directly on `<label>` elements or generic `<div>`s for engineering terms (like `E1`) lacks visual affordance for sighted users (unless they accidentally hover) and is inconsistently announced by screen readers.
**Action:** Wrap abbreviated technical terms in `<abbr title="...">` to provide standard semantic meaning, ensuring screen readers can access the expansion and browsers provide a default visual affordance (dotted underline) indicating a tooltip is available.

## 2026-03-20 - ARIA Key Shortcuts
**Learning:** Providing visual shortcut hints (e.g. `Ctrl+Enter`) inside buttons is great for sighted users but lacks programmatic exposure for assistive technologies.
**Action:** Always pair visual keyboard shortcut hints with the `aria-keyshortcuts` attribute on the target element to ensure screen readers announce the available shortcut.

## 2026-03-24 - Stateful Buttons and ARIA Labels
**Learning:** When a button briefly changes state (e.g., to "Copied!"), changing the innerHTML alone is not sufficient if the button originally relied on an `aria-label`. The `aria-label` will override the new inner text for screen readers, preventing them from hearing the success state.
**Action:** Always temporarily update the `aria-label` attribute (and restore it afterwards) when providing temporary visual state changes on buttons to ensure screen readers announce the new state.

## 2026-03-24 - D3 SVG Accessibility
**Learning:** Appending a `<title>` to a `<svg>` element generated via D3 is not sufficient for robust accessibility; many screen readers will ignore it.
**Action:** Always add an explicit ID to the appended `<title>` element and link the parent `<svg>` to it using `aria-labelledby="[id]"`.

## 2026-03-30 - Scrollable Regions and Keyboard Access
**Learning:** Elements like `<pre>` containing code or matrix outputs often become scrollable on smaller screens or when content overflows. If they lack focusability, keyboard-only users cannot scroll them to read the full content.
**Action:** Always add `tabindex="0"` to scrollable regions (like `<pre>` blocks) so they can receive keyboard focus and be scrolled using arrow keys.

## 2026-03-30 - Success Toast Color Contrast
**Learning:** Using default "success" green colors (like `#2ecc71` or `#1e8449`) on very light green backgrounds (like `#f0fdf4`) often fails WCAG AA minimum contrast ratio (4.5:1) for normal text.
**Action:** Explicitly darken success text colors (e.g., `#145c32`) when used against lightly tinted backgrounds to ensure readability for all users while maintaining the semantic color scheme.

## 2026-03-30 - Shortcut Hint Color Contrast
**Learning:** Semi-transparent white backgrounds and borders (e.g., `rgba(255, 255, 255, 0.2)`) on keyboard shortcut hints placed inside blue buttons fail WCAG AA contrast ratios because the white text blends too much with the blended background.
**Action:** Use semi-transparent black overlays (e.g., `rgba(0, 0, 0, 0.25)`) to darken the hint background against the button color, increasing the contrast of the white text.
