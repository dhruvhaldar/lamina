## 2026-03-21 - [Information Disclosure via Auto-Generated API Docs]
**Vulnerability:** The FastAPI application exposed its internal OpenAPI schema, Swagger UI (`/docs`), and ReDoc (`/redoc`) endpoints by default. This exposes the complete API surface area, parameter structures, and endpoints to attackers, significantly lowering the barrier to entry for discovering other vulnerabilities or crafting targeted attacks.
**Learning:** Default framework configurations (like FastAPI's automatic docs) are convenient for development but constitute a security risk in production environments by unnecessarily disclosing the system's architecture.

## 2024-05-31 - [Strict Pydantic Model Validation]
**Vulnerability:** Pydantic models lacked strict validation for extra fields, potentially allowing attackers to send massive or unexpected payloads to exhaust server resources or bypass validation logic.
**Learning:** By default, Pydantic ignores extra fields in models. This can lead to unexpected behavior or security issues if the API processes or stores these fields later.
**Prevention:** Add `model_config = {"extra": "forbid"}` to all Pydantic models to strictly enforce the expected schema and reject any requests containing extra fields.
