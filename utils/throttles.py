from rest_framework.throttling import SimpleRateThrottle
from utils.exceptions import RateFormatException, EndpointThrottledException


class BaseThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        indent = request.data.get("email")
        if not indent:
            if request.user.is_authenticated:
                indent = request.user.email
            else:
                indent = self.get_ident()
        return self.cache_format % {
            "scope": self.scope,
            "ident": indent.lower(),
        }

    def parse_rate(self, rate):
        """
        Parses the request rate string and returns a tuple of:
        <allowed number of requests>, <period of time in seconds>.

        Args:
            rate (str): Rate string in the format "<requests>/<time unit>".

        Returns:
            tuple: (int, int) -> <allowed number of requests>, <time in seconds>
        """

        if rate is None:
            return (None, None)

        try:
            num, period = rate.split("/")
            num_requests = int(num)

            time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
            duration = int(period[:-1]) * time_units[period[-1]]

            return num_requests, duration
        except (ValueError, KeyError):
            raise RateFormatException

    def allow_request(self, request, view):
        """
        Override to provide custom exception and status code when throttled.

        On success raises `throttle_success`.
        On failure calls `throttle_failure`.
        """
        if self.rate is None:
            return True

        self.key = self.get_cache_key(request, view)
        if self.key is None:
            return True

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()

        # Drop any requests from the history which have now passed the
        # throttle duration
        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            wait_time = int(self.wait())
            raise EndpointThrottledException(
                f"please try again in {wait_time} seconds."
            )
        return self.throttle_success() 