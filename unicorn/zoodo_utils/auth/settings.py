import importlib

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


USER_SETTINGS = getattr(settings, 'ZOODO_AUTH', None)

DEFAULTS = {
    'JWT_ISSUER': '',
    'JWT_PRIVATE_KEY': '',
}

# List of settings that cannot be empty
MANDATORY = (
    'JWT_ISSUER',
    'JWT_PRIVATE_KEY',
)


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    elif "." in val:
        return import_from_string(val, setting_name)
    else:
        raise ImproperlyConfigured("Bad value for %r: %r" % (setting_name, val))


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        parts = val.split(".")
        module_path, class_name = ".".join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except ImportError as e:
        msg = "Could not import %r for setting %r. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class ZoodoAuthSettings(object):
    """
    A settings object, that allows OAuth2 Provider settings to be accessed as properties.

    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """

    def __init__(self, user_settings=None, defaults=None, mandatory=None):
        self.user_settings = user_settings or {}
        self.defaults = defaults or {}
        self.mandatory = mandatory or ()

    def __getattr__(self, attr):
        if attr not in self.defaults.keys():
            raise AttributeError("Invalid OAuth2Provider setting: %r" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Overriding special settings
        if attr == "_SCOPES":
            val = list(self.SCOPES.keys())
        if attr == "_DEFAULT_SCOPES":
            if "__all__" in self.DEFAULT_SCOPES:
                # If DEFAULT_SCOPES is set to ["__all__"] the whole set of scopes is returned
                val = list(self._SCOPES)
            else:
                # Otherwise we return a subset (that can be void) of SCOPES
                val = []
                for scope in self.DEFAULT_SCOPES:
                    if scope in self._SCOPES:
                        val.append(scope)
                    else:
                        raise ImproperlyConfigured("Defined DEFAULT_SCOPES not present in SCOPES")

        self.validate_setting(attr, val)

        # Cache the result
        setattr(self, attr, val)
        return val

    def validate_setting(self, attr, val):
        if not val and attr in self.mandatory:
            raise AttributeError("OAuth2Provider setting: %r is mandatory" % (attr))


zoodo_auth_settings = ZoodoAuthSettings(USER_SETTINGS, DEFAULTS, MANDATORY)
