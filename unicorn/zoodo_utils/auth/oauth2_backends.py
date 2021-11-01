from oauth2_provider.oauth2_backends import OAuthLibCore
from oauth2_provider.settings import oauth2_settings

from . import tokens
from .settings import ZoodoAuthSettings


class JWTOAuthLibCore(OAuthLibCore):

    def __init__(self, server=None):
        self.server = server or oauth2_settings.OAUTH2_SERVER_CLASS(
            oauth2_settings.OAUTH2_VALIDATOR_CLASS(),
            token_generator=tokens.signed_token_generator(
                ZoodoAuthSettings.JWT_PRIVATE_KEY,
                iss=ZoodoAuthSettings.JWT_ISSUER
            )
        )
