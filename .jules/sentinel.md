## 2026-02-14 - [Path Traversal in API Endpoint]
**Vulnerability:** The `/api/read_file` endpoint blindly concatenated user-provided filename to `public/` directory path, allowing traversal via `..`.
**Learning:** Even with URL routing/normalization, raw file system access using user input MUST always be validated. FastAPI/Starlette routers do not guarantee traversal protection for file paths constructed manually.
**Prevention:** Validate resolved paths using `os.path.abspath` and check if they start with the intended base directory.

## 2026-02-14 - [DoS via Resource Exhaustion]
**Vulnerability:** The `/api/calculate` endpoint allowed arbitrarily large arrays in `stack` parameter, causing O(N) loop execution that could exhaust server CPU/memory (DoS). Additionally, invalid material properties (e.g., `v12=1`) could cause division-by-zero crashes.
**Learning:** Pydantic models by default validate *types* but not *magnitude* or *constraints*. Computational endpoints must enforce upper bounds on input sizes and validate physical constants to prevent resource exhaustion and unhandled exceptions.
**Prevention:** Use Pydantic's `@field_validator` to enforce maximum list lengths (e.g., `len(stack) <= 200`) and `@model_validator` to enforce mathematical constraints (e.g., thermodynamic stability).

## 2026-10-27 - [Path Traversal via Symlink]
**Vulnerability:** `os.path.abspath` was used to validate paths, but it does not resolve symbolic links. This allowed accessing files outside the intended directory if a symlink existed within it.
**Learning:** `os.path.abspath` normalizes `..` but preserves symlinks. `os.path.realpath` is required to resolve symlinks and ensure the *actual* file location is within the allowed directory.
**Prevention:** Always use `os.path.realpath` when validating file paths to prevent symlink attacks.
