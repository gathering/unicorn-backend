import django.dispatch

# args:
#       "metadata",
#       "filename",
#       "upload_file_path",
#       "file_size",
#       "upload_url",
#       "destination_folder",
#       "entry_id",
#       "uploader",
#       "type",
tus_upload_finished_signal = django.dispatch.Signal()
