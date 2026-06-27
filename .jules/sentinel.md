## 2026-03-21 - [Information Disclosure via Auto-Generated API Docs]
**Vulnerability:** The FastAPI application exposed its internal OpenAPI schema, Swagger UI (`/docs`), and ReDoc (`/redoc`) endpoints by default. This exposes the complete API surface area, parameter structures, and endpoints to attackers, significantly lowering the barrier to entry for discovering other vulnerabilities or crafting targeted attacks.
**Learning:** Default framework configurations (like FastAPI's automatic docs) are convenient for development but constitute a security risk in production environments by unnecessarily disclosing the system's architecture.

## 2024-05-31 - [Strict Pydantic Model Validation]
**Vulnerability:** Pydantic models lacked strict validation for extra fields, potentially allowing attackers to send massive or unexpected payloads to exhaust server resources or bypass validation logic.
**Learning:** By default, Pydantic ignores extra fields in models. This can lead to unexpected behavior or security issues if the API processes or stores these fields later.
**Prevention:** Add `model_config = {"extra": "forbid"}` to all Pydantic models to strictly enforce the expected schema and reject any requests containing extra fields.

## 2026-06-02 - [Security Headers Bypass on 500 Errors]
**Vulnerability:** The application used FastAPI's `BaseHTTPMiddleware` to append security headers (CSP, HSTS, X-Frame-Options) to all responses. However, if an unhandled exception occurred in an endpoint, it bubbled up through `call_next()`, skipping the header appending logic. The top-level ASGI exception handler would then return a 500 error response without any security headers, potentially exposing the error page to clickjacking or cross-site scripting (if default error pages reflect input).
**Learning:** In Starlette/FastAPI, `BaseHTTPMiddleware` is bypassed when an exception propagates upwards.
**Prevention:** Wrap `await call_next(request)` in a `try...except Exception as e:` block. Log the error properly (`logging.exception`) and construct a generic 500 JSON response within the exception block. This guarantees a valid response object is created and security headers are consistently appended to all responses, including server crashes.

## 2026-06-07 - [Negative Content-Length Bypass in PayloadSizeLimitMiddleware]
**Vulnerability:** The ASGI middleware designed to reject overly large payloads early (via the `Content-Length` header) failed to validate for negative values. An attacker sending a negative length (e.g., `Content-Length: -10`) would bypass the `int(content_length) > self.limit` check, pushing the malformed request to the downstream dynamic body reader.
**Learning:** Early validation checks relying on numerical bounds must explicitly handle negative or physically impossible values to prevent logical bypasses.
**Prevention:** In payload size middlewares, always add `if int(content_length) < 0` to immediately reject malformed requests with a 400 Bad Request before processing.
## 2025-06-27 - [Reflected DoS in FastAPI Validation Error Handler]
**Vulnerability:** FastAPIs default Pydantic RequestValidationError handler reflects the entire 'loc' array of invalid keys. Attackers submitting massive, undocumented string keys in the JSON payload cause Pydantic to reflect these massive strings back, triggering significant memory consumption and bandwidth saturation leading to Reflected Denial of Service (DoS).
**Learning:** Pydantic's `extra="forbid"` provides validation defense, but the resulting `RequestValidationError` still processes and returns the rejected keys verbatim. Handlers must sanitize not just the error input/URL, but the `loc` path structure as well.
**Prevention:** Always iterate through the `loc` tuples in custom `RequestValidationError` exception handlers and truncate strings to a reasonable length (e.g., 50 characters) before reflecting them in the JSONResponse.
