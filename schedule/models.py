from django.db import models
from django.contrib.auth.models import User
from kakeibo.models import Record

class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name='予定タイトル')
    start_time = models.DateTimeField(verbose_name='開始日時')
    end_time = models.DateTimeField(blank=True, null=True, verbose_name='終了日時')
    description = models.TextField(blank=True, verbose_name='説明')
    #　家計簿との連動
    related_record = models.ForeignKey(Record, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='関連家計簿')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} ({self.start_time})'
