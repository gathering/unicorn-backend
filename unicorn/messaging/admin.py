from django.contrib import admin

from .models import Message, Thread, ThreadMember

admin.site.register(Thread)
admin.site.register(ThreadMember)
admin.site.register(Message)
