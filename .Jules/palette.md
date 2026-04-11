## 2024-05-28 - Trigger Native HTML5 Validation Before API Requests
**Learning:** Even without an explicit `<form>` wrapper, native HTML5 form validation (e.g., `required`, `type="number"`) can be utilized by manually querying for invalid inputs (`document.querySelector('input:invalid, select:invalid')`) and invoking `.reportValidity()` on them. This surfaces immediate, accessible, browser-native validation tooltips instead of waiting for generic server-side validation error toasts.
**Action:** Always verify if frontend user interactions (like clicking a submit or calculate button outside of a traditional form submission) bypass native HTML5 validation. If they do, manually invoke `.reportValidity()` on invalid fields before making API requests to provide superior localized feedback.

## 2025-02-14 - Async Operation Feedback
**Learning:** Users lack visibility into long-running calculations (1-2s), leading to potential double submissions.
**Action:** Implement a reusable `setLoading` helper for all async buttons to manage disabled state, aria-busy, and visual spinner.

## 2025-03-10 - Input Handling for Lists
**Learning:** Users often copy-paste list data (like stacking sequences) in various formats (space-separated vs. comma-separated). Strict comma-only parsing leads to silent data dropping or errors.
**Action:** Use regex-based splitting (`/[\s,]+/`) when parsing text inputs representing numerical lists to robustly handle spaces, commas, or combinations of both, ensuring data integrity regardless of input format.

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

## 2026-03-11 - Preserving CSS Grid Layouts During Label Upgrades
**Learning:** When upgrading implicitly wrapped labels (e.g., `<label>Text <input></label>`) to explicitly associated ones (using `for` and `id`), moving the `<input>` element outside of the `<label>` wrapper can break existing CSS Grid or Flexbox layouts that treat the original `<label>` as a single unified layout container.
**Action:** When adding `for` attributes to explicitly link inputs for screen readers, carefully maintain the original nested HTML structure (e.g., `<label for="id">Text <input id="id"></label>`) unless CSS rules are also being refactored to accommodate separated elements.

## 2026-03-12 - Aligning Native and Custom Validation States
**Learning:** Pre-submission validation functions that only query for native `:invalid` states will fail to catch fields flagged by custom JavaScript validation (`aria-invalid="true"`), resulting in unnecessary API calls and generic server-side errors rather than utilizing existing real-time inline feedback.
**Action:** Always include `[aria-invalid="true"]` selectors when checking form validity before submission. If native `reportValidity()` cannot be invoked, manually call `.focus()` on the invalid element to direct the user's attention to the inline accessibility error message.

## 2026-03-18 - Checkbox and Radio Button Styling
**Learning:** Applying `width: 100%` globally to the `input` selector causes checkboxes and radio buttons to stretch across their containers, severely breaking the layout and looking unpolished.
**Action:** Always use `:not([type="checkbox"]):not([type="radio"])` or more specific attribute selectors (like `input[type="text"]`, `input[type="number"]`) when applying global sizing rules (like `width: 100%` or heavy padding) to inputs. Add specific blocks for checkboxes to ensure `width: auto` and proper vertical alignment.

## 2026-04-02 - Number Input Scroll Wheel Hijacking
**Learning:** HTML `<input type="number">` elements hijack the mouse scroll wheel to increment/decrement values when focused. In engineering applications where inputs contain large scientific notation values (e.g., `140e9`), scrolling accidentally increments the value by 1 (e.g., `140000000001`), which is mathematically useless and corrupts user data without obvious visual indication.
**Action:** Always add a global `wheel` event listener that blurs focused number inputs to prevent accidental value manipulation and allow normal, safe page scrolling.

## 2026-05-15 - Responsive CSS Grid on Mobile Viewports
**Learning:** Defining grid template columns with fixed pixel minimums using `minmax(Xpx, 1fr)` (e.g. `minmax(400px, 1fr)`) causes elements to overflow their containers on mobile devices with viewport widths smaller than the fixed minimum. This leads to broken layouts and unwanted horizontal scrolling.
**Action:** Use `minmax(min(100%, Xpx), 1fr)` when configuring responsive grid columns. This allows grid items to gracefully shrink below their target width on small mobile viewports, while maintaining the intended layout on larger screens.

## 2026-06-12 - Implicit Form Submission
**Learning:** Users instinctively press `Enter` after filling an input field, expecting the primary action (like calculation) to execute. When inputs are not wrapped in a native `<form>` element, this behavior is lost, leading to friction as users are forced to manually click the primary button.
**Action:** When a `<form>` cannot be used, implement an event listener for `Enter` on `input` and `select` elements to manually trigger the primary action, restoring expected user behavior.

## 2026-07-15 - Abbreviation Discoverability
**Learning:** By default, HTML `<abbr title="...">` tags do not change the mouse cursor to a question mark or help pointer on hover in all browsers, making their tooltips difficult for sighted users to discover.
**Action:** Always apply `cursor: help` and explicit dotted underlines (using `text-decoration` properties) to `<abbr[title]>` elements to ensure their interactive nature is visually apparent.

## 2026-03-28 - Visual Hierarchy for Action Buttons
**Learning:** Presenting multiple action buttons with identical primary visual weight (e.g., solid brand color backgrounds) creates cognitive load and fails to guide the user toward the primary intended action.
**Action:** Always establish a clear visual hierarchy by reserving solid/heavy styles for the primary action and using outlined or subtle background styles for secondary or alternative actions.

## 2026-08-01 - Accessible Ephemeral Notifications
**Learning:** Automatically disappearing toast notifications violate WCAG "Timing Adjustable" constraints if users (especially those using screen readers or with cognitive disabilities) cannot pause the timer to read the content or manually dismiss it.
**Action:** Always include an interactive, accessible dismiss button (`aria-label`) on toast notifications to give users explicit control over dismissing the alert. Additionally, never use auto-dismiss timeouts for toast notifications; always rely on manual dismissal to ensure compliance.

## 2026-08-05 - Skip-to-Content Link for Keyboard Navigation
**Learning:** Users relying heavily on keyboard navigation are forced to tab through all header/navigation links repeatedly on every page load unless a bypass mechanism is provided.
**Action:** Always include a visually hidden but focusable `<a class="skip-link" href="#main-content">Skip to main content</a>` at the top of the body that points to a `tabindex="-1"` element like `<main id="main-content">` to allow users to bypass repetitive content. Remove the default focus outline from `#main-content` to avoid an unpleasant visual state when focused programmatically.

## 2026-03-30 - Focus Management During Async Loading
**Learning:** Setting the native `disabled` attribute on an element (like a submit button) while it performs an async action immediately removes it from the document's tab order and forces it to lose focus. For keyboard and screen reader users, this is highly disorienting because their focus is reset to the top of the `<body>`, forcing them to navigate through the entire page again to see the results.
**Action:** Use `aria-disabled="true"` instead of `disabled` during async states to visually and semantically communicate the disabled state without stealing keyboard focus. Remember to manually block `click` and `keydown` events when `aria-disabled="true"` is set.

## 2026-04-03 - Accessible Ephemeral Notifications Revision
**Learning:** Even with an accessible manual dismiss button, automatically disappearing toast notifications still violate WCAG "Timing Adjustable" constraints if users (especially those using screen readers or with cognitive disabilities) cannot read the content before it disappears.
**Action:** Never use auto-dismiss timeouts (`setTimeout`) for toast notifications. Always rely exclusively on manual dismissal.

## 2026-04-10 - Elevating Custom Validation to Native UI
**Learning:** Custom Javascript validation using purely visual cues and ARIA attributes (like `aria-invalid`) fails to provide the localized popup tooltip feedback that native HTML5 validation offers (e.g. `reportValidity()`). If a custom validation fails, users don't see the specific error attached to the input natively, forcing a reliance on fallback methods like `.focus()`.
**Action:** Use `input.setCustomValidity(message)` when a custom Javascript validation fails (e.g. empty sequence, specific numeric constraint) and `input.setCustomValidity('')` when it passes. This bridges the gap, allowing `reportValidity()` to natively render accessible, localized error tooltips containing your specific error message instead of generic messages or silent focusing.

## 2026-08-10 - Hiding Spin Buttons on Engineering Numeric Inputs
**Learning:** Native browser spin buttons (up/down arrows) on `<input type="number">` are detrimental in engineering applications dealing with large scientific notation values (e.g., `140e9`). Clicking these arrows increments/decrements the value by 1 (e.g., `140000000001`), which is mathematically negligible, clutters the UI, and can confuse users.
**Action:** Always hide the native spin buttons using `::-webkit-inner-spin-button`, `::-webkit-outer-spin-button`, and `-moz-appearance: textfield` via CSS for number inputs in engineering/scientific contexts.

## 2026-08-11 - Disabling Arrow Keys on Engineering Numeric Inputs
**Learning:** Even with spin buttons hidden, pressing `ArrowUp` or `ArrowDown` while a `<input type="number">` is focused still alters the value. In engineering applications dealing with large scientific notation values, this leads to negligible changes (e.g., incrementing `140e9` by 1) that corrupt data without obvious visual indication.
**Action:** Always add a global `keydown` event listener that intercepts `ArrowUp` and `ArrowDown` on focused number inputs and calls `e.preventDefault()` to avoid accidental data manipulation.
