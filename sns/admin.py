from django.contrib import admin
from .models import Post, Message, Comment, Attachment, Notification

admin.site.register(Post)
admin.site.register(Message)
admin.site.register(Comment)
admin.site.register(Attachment)
admin.site.register(Notification)
