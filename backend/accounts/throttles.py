from rest_framework.throttling import AnonRateThrottle
from django.conf import settings


class LoginThrottle(AnonRateThrottle):
    scope = "login"

    def get_rate(self):
        """Return the throttle rate for the 'login' scope.

        DRF expects DEFAULT_THROTTLE_RATES to be available under
        settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] (a dict). Use
        dict access to avoid getattr on a dict which returns None.
        """
        rest = getattr(settings, 'REST_FRAMEWORK', None)
        if isinstance(rest, dict):
            rates = rest.get('DEFAULT_THROTTLE_RATES', {})
        else:
            rates = {}
        return rates.get(self.scope)