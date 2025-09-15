from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True, verbose_name='自己紹介')
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    followers = models.ManyToManyField(User, related_name='following_profiles', blank=True)

    def __str__(self):
        return f'{self.user}のプロフィール'
    
    def followers_count(self):
        return self.followers.count()

    def following_count(self):
        return self.user.following_profiles.count()