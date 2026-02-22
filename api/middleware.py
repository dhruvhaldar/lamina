from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from fastapi import Request, Response
import time

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # CSP: allow scripts from self and d3js (CDN), allow unsafe-inline for now as frontend relies on it
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://d3js.org; style-src 'self' 'unsafe-inline'; img-src 'self' data:"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit=100, window=60):
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.clients = {} # ip -> (count, start_time)

    async def dispatch(self, request: Request, call_next):
        # Use request.client.host which is populated by the ASGI server (Uvicorn/Vercel)
        # using trusted proxy headers. This avoids IP spoofing via X-Forwarded-For injection.
        if request.client and request.client.host:
            ip = request.client.host
        else:
            ip = "unknown"

        now = time.time()

        # Cleanup if cache grows too large (simple protection against memory exhaustion)
        if len(self.clients) > 10000:
            # Secure cleanup: Remove expired entries instead of clearing all (fail-secure)
            # This prevents an attacker from resetting the limit by filling the cache
            expired = [ip for ip, (count, start) in self.clients.items() if now > start + self.window]
            for ip in expired:
                del self.clients[ip]

            # If still too large, remove oldest entries (FIFO) to maintain memory bounds
            if len(self.clients) > 10000:
                # Remove first 100 entries (approx. 1% of cache)
                # Python dicts preserve insertion order, so keys are ordered by insertion time
                keys = list(self.clients.keys())
                for k in keys[:100]:
                    del self.clients[k]

        # Get current usage
        # Default start_time is now if new IP
        count, start_time = self.clients.get(ip, (0, now))

        # Check if window expired
        if now > start_time + self.window:
            count = 1
            start_time = now
        else:
            count += 1

        if count > self.limit:
            return Response("Too Many Requests", status_code=429)

        self.clients[ip] = (count, start_time)
        return await call_next(request)
