from urllib.request import build_opener
from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作成者')
    title = models.CharField(max_length=100, verbose_name='タイトル')
    content = models.TextField(verbose_name='本文')
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='likes_posts', blank=True)

    def __str__(self):
        return f'{self.author.username} の {self.title} 投稿'

    def like_count(self):
        return self.likes.count()
    
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=100, verbose_name='件名')
    body = models.TextField(verbose_name='メッセージ')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    is_update = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} ({self.sender} → {self.recipient})"

class Attachment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='message_files')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField(verbose_name='コメント')
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)

    def __str__(self):
        return f'{self.user.username}: {self.body[:20]}'
    
    def like_count(self):
        return self.likes.count()

class Notification(models.Model):
    NOTIFICATION_TYPE = (
        ('like_post', 'いいね（投稿）'),
        ('like_comment', 'いいね（コメント）'),
        ('comment', 'コメント'),
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender} → {self.recipient} ({self.notification_type})'
