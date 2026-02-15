## 2026-02-14 - [Path Traversal in API Endpoint]
**Vulnerability:** The `/api/read_file` endpoint blindly concatenated user-provided filename to `public/` directory path, allowing traversal via `..`.
**Learning:** Even with URL routing/normalization, raw file system access using user input MUST always be validated. FastAPI/Starlette routers do not guarantee traversal protection for file paths constructed manually.
**Prevention:** Validate resolved paths using `os.path.abspath` and check if they start with the intended base directory.

## 2026-02-14 - [DoS via Resource Exhaustion]
**Vulnerability:** The `/api/calculate` endpoint allowed arbitrarily large arrays in `stack` parameter, causing O(N) loop execution that could exhaust server CPU/memory (DoS). Additionally, invalid material properties (e.g., `v12=1`) could cause division-by-zero crashes.
**Learning:** Pydantic models by default validate *types* but not *magnitude* or *constraints*. Computational endpoints must enforce upper bounds on input sizes and validate physical constants to prevent resource exhaustion and unhandled exceptions.
**Prevention:** Use Pydantic's `@field_validator` to enforce maximum list lengths (e.g., `len(stack) <= 200`) and `@model_validator` to enforce mathematical constraints (e.g., thermodynamic stability).
