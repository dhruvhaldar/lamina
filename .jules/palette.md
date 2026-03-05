## 2026-03-05 - Destroying Accessibility Hints via innerText
**Learning:** Overwriting a button's `innerText` (e.g., during loading states) destroys internal HTML elements like spans used for keyboard hints (`<span class="shortcut-hint" aria-hidden="true">`), permanently breaking visual UX and accessibility features after a single interaction.
**Action:** Always store and restore `innerHTML` (or use CSS pseudo-elements/hidden spans) when manipulating button states to preserve internal DOM structure and ARIA attributes.

## 2026-03-05 - Making Dynamic Inline Validation Accessible
**Learning:** Visual-only inline validation errors (e.g., turning text red and updating a sibling `div` with an error message) are invisible to screen readers unless explicitly linked.
**Action:** When creating dynamic error message containers, add `aria-live="polite"` and dynamically link the container's ID to the input's `aria-describedby` attribute to ensure AT users are informed of validation failures as they type.
