from urllib import response
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.views import View
from django.core.exceptions import PermissionDenied
from .models import Post, Message, Attachment
from .forms import PostCreateForm, MessageForm

def index_view(request):
    return render(request, 'sns/index.html')

class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'sns/post_list.html'

class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'sns/post_detail.html'

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'sns/post_create.html'
    form_class = PostCreateForm
    success_url = reverse_lazy('sns:post_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'sns/post_update.html'
    form_class = PostCreateForm

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.author != self.request.user:
            raise PermissionDenied
        return obj
    
    def get_success_url(self):
        return reverse('sns:post_detail', kwargs={'pk': self.object.pk})

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'sns/post_delete.html'
    success_url = reverse_lazy('sns:post_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.author != self.request.user:
            raise PermissionDenied
        return obj

class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    template_name = 'sns/message_create.html'
    form_class = MessageForm
    success_url = reverse_lazy('sns:message_inbox')

    def form_valid(self, form):
        form.instance.sender = self.request.user
        response = super().form_valid(form)
        # 複数ファイルをまとめて取得
        files = self.request.FILES.getlist('files')
        for f in files:
            Attachment.objects.create(message=self.object, file=f)
        return response

class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    template_name = 'sns/message_update.html'
    form_class = MessageForm

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.sender != self.request.user:
            raise PermissionDenied
        return obj
    
    def form_valid(self, form):
        form.instance.is_update = True
        response = super().form_valid(form)
        # 新規ファイルの追加
        files = self.request.FILES.getlist('files')
        for f in files:
            Attachment.objects.create(message=self.object, file=f)
        return response
    
    def get_success_url(self):
        return reverse('sns:message_detail', kwargs={'pk': self.object.pk})

class MessageDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        message= get_object_or_404(Message, pk=pk)
        return render(request, 'sns/message_delete.html', {'message': message})
    
    def post(self, request, pk):
        message = get_object_or_404(Message, pk=pk)
        if message.sender != request.user:
            raise PermissionDenied
        message.is_update = True
        message.body = 'このメッセージは削除されました。'
        message.save()
        return redirect('sns:message_detail', pk=pk)
    
class MessageInboxView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'sns/message_inbox.html'

    def get_queryset(self):
        return Message.objects.filter(recipient=self.request.user).order_by('-created_at')

class MessageOutboxView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'sns/message_outbox.html'

    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user).order_by('-created_at')

class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'sns/message_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # 自分が送信者、受信者でなければ権限なしのエラーメッセージ
        if obj.recipient != self.request.user and obj.sender != self.request.user:
            raise PermissionDenied
        # 未読から既読に変更
        if obj.recipient == self.request.user and not obj.is_read:
            obj.is_read = True
            obj.save()
        return obj

class MessageReplyView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'sns/message_reply.html'

    def dispatch(self, request, *args, **kwargs):
        self.origin_message = get_object_or_404(Message, pk=kwargs['pk'])
        if self.origin_message.recipient != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        # 初期値（宛先と件名）を設定
        initial = super().get_initial()
        initial['recipient'] = self.origin_message.sender
        initial['subject'] = f'Re: {self.origin_message.subject}'
        return initial
    
    def form_valid(self, form):
        form.instance.sender = self.request.user
        form.instance.recipient = self.origin_message.sender
        response = super().form_valid(form)

        files = self.request.FILES.getlist('files')
        for f in files:
            Attachment.objects.create(message=self.object, file=f)
        return response
    
    def get_success_url(self):
        return reverse('sns:message_inbox')

class MessageForwardView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'sns/message_forward.html'

    def dispatch(self, request, *args, **kwargs):
        self.origin_message = get_object_or_404(Message, pk=kwargs['pk'])
        if self.origin_message.sender != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        initial = super().get_initial()
        initial['subject'] = f'Fwd: {self.origin_message.subject}'
        initial['body'] = (
            f'\n\n---- Original Message ----\n'
            f'From: {self.origin_message.sender}\n'
            f'To: {self.origin_message.recipient}\n'
            f'Date: {self.origin_message.created_at}\n\n'
            f'{self.origin_message.body}'
        )
        return initial
    
    def form_valid(self, form):
        form.instance.sender = self.request.user
        response = super().form_valid(form)

        files = self.request.FILES.getlist('files')
        for f in files:
            Attachment.objects.create(message=self.object, file=f)
        return response
    
    def get_success_url(self):
        return reverse('sns:message_outbox')
    
class AttachmentDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        attachment = get_object_or_404(Attachment, pk=pk)
        if attachment.message.sender != request.user:
            raise PermissionDenied
        
        message_pk = attachment.message.pk
        attachment.delete()
        return redirect('sns:message_update', pk=message_pk)