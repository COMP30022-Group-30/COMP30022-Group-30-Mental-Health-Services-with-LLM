from __future__ import annotations

from rest_framework.throttling import SimpleRateThrottle


class AdminLoginRateThrottle(SimpleRateThrottle):
    """
    Rate limits repeated login attempts against the admin authentication endpoint.
    """

    scope = "admin_login"

    def get_cache_key(self, request, view):
        if not request:
            return None
        ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}
