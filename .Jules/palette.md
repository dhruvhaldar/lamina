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
