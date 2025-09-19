from django.db import models
from django.contrib.auth.models import User

class Record(models.Model):
    CATEGORY_CHOICES = (
        ('income', '収入'),
        ('expense', '支出'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ユーザー')
    date = models.DateField(verbose_name='日付')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='区分')
    amount = models.IntegerField(verbose_name='金額')
    memo = models.TextField(blank=True, null=True, verbose_name='メモ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日')

    def __str__(self):
        return f'{self.date} - {self.get_category_display()} {self.amount} 円'

