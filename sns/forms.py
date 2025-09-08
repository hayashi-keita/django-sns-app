from django import forms
from .models import Post, Message, Comment
from django.contrib.auth.models import User

class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']

class MessageForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(queryset=User.objects.all(), label='宛先')
    # 単発ファイルフィールド（複数はJSで追加）
    files = forms.FileField(
        required=False,
        label='添付ファイル'
    )
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 2, 'placeholder': 'コメントを入力...'})
        }