from rest_framework.throttling import AnonRateThrottle
from rest_framework.exceptions import Throttled

class LoginThrottle(AnonRateThrottle):
    scope = "login"

    def throttle_failure(self):
        exc = Throttled(wait=self.wait())
        exc.scope_name = self.scope
        raise exc