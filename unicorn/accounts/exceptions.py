from social_core.exceptions import AuthException


class AuthRejected(AuthException):
    """Backend is not available for new users."""

    def __init__(self, backend_name):
        self.backend_name = backend_name

    def __str__(self):
        return f"Backend '{self.backend_name}' is only available for existing users."


class AuthRejectedNoTicket(AuthException):
    """Backend reports the user to not have a valid ticket"""

    def __str__(self):
        return "Sorry, your account does not have a valid ticket for this event."
