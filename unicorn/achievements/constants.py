from django.utils.translation import ugettext_lazy as _


ACHIEVEMENT_TYPE_PARTICIPANT = 1
ACHIEVEMENT_TYPE_CREW = 2
ACHIEVEMENT_TYPE_CHOICES = (
    (ACHIEVEMENT_TYPE_PARTICIPANT, _("Participant")),
    (ACHIEVEMENT_TYPE_CREW, _("Crew")),
)
