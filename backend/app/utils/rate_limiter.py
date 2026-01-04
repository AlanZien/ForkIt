"""Rate limiting utilities for API endpoints.

Uses slowapi for request rate limiting.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)

# Pre-defined rate limit strings
AUTH_RATE_LIMIT = f"{settings.rate_limit_requests}/minute"
VERIFICATION_RATE_LIMIT = "3/hour"
