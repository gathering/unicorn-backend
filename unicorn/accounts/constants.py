from django.utils.translation import gettext_lazy as _

# User genders
USER_GENDER_OTHER = "other"
USER_GENDER_MALE = "male"
USER_GENDER_FEMALE = "female"
USER_GENDERS = (
    (USER_GENDER_OTHER, _("Other/ Prefer not say")),
    (USER_GENDER_MALE, _("Male")),
    (USER_GENDER_FEMALE, _("Female")),
)

# User roles
USER_ROLE_CREW = "crew"
USER_ROLE_PARTICIPANT = "participant"
USER_ROLE_JURY = "jury"
USER_ROLE_ANON = "anon"
USER_ROLE_MORTAL = "mortal"
USER_ROLE_CHOICES = (
    (USER_ROLE_CREW, _("Crew")),
    (USER_ROLE_PARTICIPANT, _("Participant")),
    (USER_ROLE_JURY, _("Jury")),
    (USER_ROLE_ANON, _("Anonymous")),
    (USER_ROLE_MORTAL, _("Other")),
)

# Displayname formats
USER_DISPLAY_FIRST_LAST = "fl"
USER_DISPLAY_LAST_FIRST = "lf"
USER_DISPLAY_FIRST_LAST_AKA = "fla"
USER_DISPLAY_LAST_FIRST_AKA = "lfa"
USER_DISPLAY_FIRST_AKA = "fa"
USER_DISPLAY_FIRST = "f"
USER_DISPLAY_AKA = "a"
USER_DISPLAY_CHOICES = (
    (USER_DISPLAY_FIRST_LAST, _("%(first)s %(last)s")),
    (USER_DISPLAY_LAST_FIRST, _("%(last)s, %(first)s")),
    (USER_DISPLAY_FIRST_LAST_AKA, _("%(first)s %(last)s aka. %(nick)s")),
    (USER_DISPLAY_LAST_FIRST_AKA, _("%(last)s, %(first)s aka. %(nick)s")),
    (USER_DISPLAY_FIRST_AKA, _("%(first)s aka. %(nick)s")),
    (USER_DISPLAY_FIRST, _("%(first)s")),
    (USER_DISPLAY_AKA, _("%(nick)s")),
)
