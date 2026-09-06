# Rate limiting setup (slowapi)
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Sensitive endpoints get explicit limits; tune these to your needs.
# NOTE: the default backend is in-memory and therefore per-process. If you run
# multiple workers/processes, swap get_remote_address for a Redis-backed key_func.
LOGIN_RATE_LIMIT = "5/minute"
REGISTER_RATE_LIMIT = "3/minute"
