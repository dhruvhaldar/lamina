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

## 2026-10-27 - [Insecure Error Handling & File Serving]
**Vulnerability:** The `/api/read_file` endpoint returned 200 OK with a JSON error message for blocked requests, confusing security scanners and clients. It also lacked `X-Content-Type-Options: nosniff` and CSP headers, increasing XSS risk for served HTML files.
**Learning:** Security controls must fail securely with appropriate HTTP status codes (403/404). File serving endpoints must include security headers to prevent MIME-sniffing and XSS.
**Prevention:** Raise `HTTPException(status_code=403)` for access violations. Use `os.path.commonpath` for robust path validation. Add `X-Content-Type-Options: nosniff` and `Content-Security-Policy` headers to file responses.

## 2026-02-20 - [IP Spoofing in Rate Limiting]
**Vulnerability:** The rate limiting middleware blindly trusted the first IP in the `X-Forwarded-For` header, allowing attackers to bypass the limit by injecting a fake IP (e.g., `X-Forwarded-For: 1.2.3.4`).
**Learning:** In a proxied environment (like Vercel/AWS), the application receives a list of IPs in `X-Forwarded-For`. The first IP is often the client-provided (untrusted) one.
**Prevention:** Rely on the infrastructure (ASGI server/Load Balancer) to resolve the client IP into `request.client.host` using trusted proxy configuration (e.g., `--proxy-headers` in Uvicorn), or parse `X-Forwarded-For` carefully by taking the rightmost trusted IP.

## 2025-02-14 - Rate Limit Cache Clearing Vulnerability
**Vulnerability:** The rate limiting middleware used a fail-open strategy that cleared the *entire* client cache when it reached capacity (10,000 entries). This allowed attackers to bypass rate limits by intentionally flooding the cache with requests from spoofed or distributed IPs.
**Learning:** A mechanism designed for memory safety (preventing resource exhaustion) can inadvertently become a security vulnerability if it indiscriminately discards security state (rate limit counters).
**Prevention:** Use targeted eviction strategies (e.g., removing expired entries first, then evicting oldest/LRU) instead of full cache clearing. Ensure that safety mechanisms do not compromise security controls.

## 2026-06-25 - [XSS Prevention via strict CSP]
**Vulnerability:** The Content Security Policy (CSP) allowed `'unsafe-inline'` in `script-src` to support legacy inline event handlers (e.g., `onclick="..."`). This significantly weakened XSS protection by allowing any injected script to execute.
**Learning:** Modern frontend frameworks and even vanilla JS should avoid inline event handlers. Refactoring legacy code to use `addEventListener` enables a stricter CSP that blocks all inline scripts, mitigating XSS risks even if injection occurs.
**Prevention:** Remove `'unsafe-inline'` from `script-src` in CSP. Move all JavaScript logic to external files and use `addEventListener` for event handling.
