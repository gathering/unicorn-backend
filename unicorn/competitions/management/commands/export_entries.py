import os
import shutil

from competitions.constants import ENTRY_STATUS_QUALIFIED
from competitions.models import Competition, Contributor
from django.core.management.base import BaseCommand
from django.db.models import Q


class Command(BaseCommand):
    help = "Runs through all entries exports them for distribution"

    def handle(self, *args, **kwargs):
        # check base path and create if it isn't there
        base_path = "/export"
        if not os.path.exists(base_path):
            self.stdout.write("+ Base directory does not exist, creating..")
            try:
                os.mkdir(base_path)
            except OSError:
                self.stderr.write("!! Failed to create base directory")
                return

        # then start by looping through all competitions
        for compo in Competition.objects.filter(Q(published=True), ~Q(fileupload="[]")):
            self.stdout.write("- Starting on competition '{}'".format(compo.name))

            # strip all kinds of special characters from the compo name and create a folder
            compo_dir = base_path + "/" + "".join(char for char in compo.name if char.isalnum())
            if not os.path.exists(compo_dir):
                self.stdout.write("+ Competition directory does not exist, creating..")
                try:
                    os.mkdir(compo_dir)
                except OSError:
                    self.stderr.write("!! Failed to create directory for competition {}".format(compo.name))
                    continue

            for entry in compo.entries.filter(status=ENTRY_STATUS_QUALIFIED):
                self.stdout.write("-- Fetching entry '{}'".format(entry.title))

                # skip if no files are present
                if not entry.files.filter(active=True).exists():
                    self.stderr.write("!! No active files found, skipping..")
                    continue

                # build some names
                title = "".join(char for char in entry.title if char.isalnum() or char == " ")
                owner_obj = Contributor.objects.get(entry=entry, is_owner=True)
                name = owner_obj.user.display_name
                owner = "".join(char for char in name if char.isalnum() or char == " ")

                # figure out which file to use
                f = entry.files.filter(active=True)
                if f.count() > 1:
                    f = f.filter(type="main")

                # extract file ending
                f = f.first()
                ending = f.file.name[f.file.name.rfind(".") :]

                # build new path and copy file
                file_path = compo_dir + "/" + title + " by " + owner + ending
                shutil.copy(f.file.path, file_path.replace(" ", "_"))
                self.stdout.write("++ Copied {} MB file".format(str(round(f.file.size / 1024 / 1024, 2))))
