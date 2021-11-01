from social_core.tests.test_exceptions import BaseExceptionTestCase

from ..exceptions import AuthRejected


class AuthRejectedTest(BaseExceptionTestCase):
    exception = AuthRejected("foobar")
    expected_message = "Backend 'foobar' is only available for existing users."
