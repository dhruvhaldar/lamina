## 2025-02-14 - Async Operation Feedback
**Learning:** Users lack visibility into long-running calculations (1-2s), leading to potential double submissions.
**Action:** Implement a reusable  helper for all async buttons to manage disabled state, aria-busy, and visual spinner.
## 2025-02-14 - Async Operation Feedback
**Learning:** Users lack visibility into long-running calculations (1-2s), leading to potential double submissions.
**Action:** Implement a reusable `setLoading` helper for all async buttons to manage disabled state, aria-busy, and visual spinner.

## 2026-02-15 - Error Feedback
**Learning:** Generic `alert()` messages ("Check inputs") frustrate users when backend provides specific validation details (e.g. "E1 must be positive").
**Action:** Replace `alert()` with a Toast notification system that parses and displays specific backend validation errors inline.

## 2026-02-16 - Technical Context
**Learning:** Users struggle with abbreviated engineering terms (`E1`, `G12`) without inline explanations, leading to confusion.
**Action:** Use `title` attributes on labels to provide full descriptive names for technical parameters without cluttering the UI.

## 2026-02-17 - Input Formatting Guidance
**Learning:** Users can find inputs with specific formatting requirements (like comma-separated lists) ambiguous without explicit examples.
**Action:** Added helper text with `aria-describedby` to provide clear formatting instructions and associate them programmatically for screen readers.

## 2026-02-18 - Result Portability
**Learning:** Users analyzing matrix data often need to transfer results to external tools, and manual selection is error-prone.
**Action:** Implement "Copy to Clipboard" actions with visual feedback ("Copied!") for all preformatted data outputs.

## 2026-02-19 - Scientific Notation Verification
**Learning:** Users struggle to verify correct entry of scientific notation (e.g., distinguishing `14e9` from `1.4e9`), leading to order-of-magnitude errors.
**Action:** Implement a real-time "Input Preview" that formats scientific values into human-readable engineering units (e.g., `14 GPa`) alongside the raw input.

## 2026-02-21 - Copying Complex Layouts
**Learning:** Visual grids (like property lists) are hard to copy cleanly.
**Action:** Use a hidden `.clipboard-data` element with pre-formatted text as a source for clipboard actions, decoupling presentation from data portability.

## 2026-02-22 - Laminate Visualization
**Learning:** Users configuring laminate stacks struggle to visualize the final configuration (symmetry, total thickness) from a raw string of angles, leading to design errors.
**Action:** Implement a real-time "Laminate Code Preview" that parses the input and displays standard engineering notation (e.g., `[0/90]s`) and physical thickness (e.g., `500 µm`) alongside the input.

## 2026-02-23 - Material Presets
**Learning:** Users hesitate to start from scratch with blank or default values, often needing standard reference points (like Carbon/Epoxy).
**Action:** Implement a "Material Library" dropdown that pre-fills standard values, reducing friction and errors.

## 2026-02-24 - Keyboard Efficiency
**Learning:** Power users (engineers) find repetitive mouse clicks for calculation inefficient and prefer keyboard-first workflows.
**Action:** Implement global keyboard shortcuts (e.g., Ctrl+Enter) with discoverable visual hints (badges) on the primary action buttons.

## 2026-02-25 - Real-time Input Validation
**Learning:** Validating complex inputs (like lists) only on submission frustrates users who must correct errors after the fact.
**Action:** Implement real-time validation in input previews to provide immediate, specific error feedback (e.g. "Invalid angle") before submission.

## 2026-02-26 - Accessible Error States
**Learning:** Setting `aria-invalid="true"` alone is insufficient; sighted users need corresponding visual cues to identify the exact field in error among many inputs.
**Action:** Always pair `aria-invalid` attributes with global CSS rules that apply a visible error state (e.g., red border/outline) to ensure all users receive equivalent feedback.
## 2026-03-01 - Tactile Feedback and Consistency
**Learning:** Users lack immediate visual confirmation when clicking buttons, and native `select` elements appear unstyled and lack clear keyboard focus indicators compared to text inputs.
**Action:** Add `button:active { transform: scale(0.98); }` for click feedback and apply consistent styling and `:focus-visible` outlines to `select` elements.

## 2026-03-02 - Accessible Color Contrast in Primary/Success States
**Learning:** Default primary action blues (e.g., `#3498db`) and success greens (e.g., `#27ae60`) often fail WCAG AA 4.5:1 contrast requirements when used as text colors on light backgrounds, making error/success states or badges illegible.
**Action:** Always verify contrast ratios for dynamic textual feedback and explicitly darken brand or standard colors (e.g., using `#2579b0` for primary, `#1e8449` for success) to ensure readability for all users.

## 2026-03-06 - SVG Accessibility and Screen Readers
**Learning:** Complex D3 visualizations generated as `<svg>` elements are opaque to screen readers by default. Conversely, decorative inline SVGs inside buttons with `aria-label`s cause redundant announcements and focus issues in older browsers.
**Action:** Always add `role="img"`, `aria-label`, and embedded `<title>` tags to informative SVG charts. For decorative SVGs inside actionable elements, always apply `aria-hidden="true"` and `focusable="false"`.

## 2026-03-07 - Real-time Accessible Inline Validation
**Learning:** Providing real-time visual formatting alongside numeric inputs using `aria-hidden` makes it opaque to screen reader users, and failing to provide immediate inline validation for incorrect inputs (like negative values or empty stacks) before submission frustrates users.
**Action:** Replace `aria-hidden` with `aria-live="polite"` and `aria-atomic="true"`, link the preview element to the input using `aria-describedby`, and provide immediate real-time validation (including changing text color and setting `aria-invalid="true"`) for improved accessibility and user experience.

## 2025-03-10 - Input Handling for Lists
**Learning:** Users often copy-paste list data (like stacking sequences) in various formats (space-separated vs. comma-separated). Strict comma-only parsing leads to silent data dropping or errors.
**Action:** Use regex-based splitting (`/[\s,]+/`) when parsing text inputs representing numerical lists to robustly handle spaces, commas, or combinations of both, ensuring data integrity regardless of input format.

## 2026-03-11 - Preserving CSS Grid Layouts During Label Upgrades
**Learning:** When upgrading implicitly wrapped labels (e.g., `<label>Text <input></label>`) to explicitly associated ones (using `for` and `id`), moving the `<input>` element outside of the `<label>` wrapper can break existing CSS Grid or Flexbox layouts that treat the original `<label>` as a single unified layout container.
**Action:** When adding `for` attributes to explicitly link inputs for screen readers, carefully maintain the original nested HTML structure (e.g., `<label for="id">Text <input id="id"></label>`) unless CSS rules are also being refactored to accommodate separated elements.
## 2024-05-28 - Trigger Native HTML5 Validation Before API Requests
**Learning:** Even without an explicit `<form>` wrapper, native HTML5 form validation (e.g., `required`, `type="number"`) can be utilized by manually querying for invalid inputs (`document.querySelector('input:invalid, select:invalid')`) and invoking `.reportValidity()` on them. This surfaces immediate, accessible, browser-native validation tooltips instead of waiting for generic server-side validation error toasts.
**Action:** Always verify if frontend user interactions (like clicking a submit or calculate button outside of a traditional form submission) bypass native HTML5 validation. If they do, manually invoke `.reportValidity()` on invalid fields before making API requests to provide superior localized feedback.
