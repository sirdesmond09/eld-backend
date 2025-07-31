from rest_framework.throttling import UserRateThrottle


class PasswordResetThrottle(UserRateThrottle):
    """Throttle for password reset requests."""
    rate = "3/hour"


class ResendEmailTokenThrottle(UserRateThrottle):
    """Throttle for resending email verification tokens."""
    rate = "5/hour" 