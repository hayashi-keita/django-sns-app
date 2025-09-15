from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView, UpdateView, DateDetailView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SignupForm, ProfileForm
from .models import Profile
from sns.models import Notification

class SignupView(CreateView):
    model = User
    template_name = 'accounts/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('sns:index')

class ProfileListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'accounts/profile_list.html'
    # 検索機能
    def get_queryset(self):
        queryset = Profile.objects.all()
        q = self.request.GET.get('q')  #検索ワード
        if q:
            queryset = queryset.filter(user__username__icontains=q) | queryset.filter(bio__icontains=q)
        return queryset

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile_detail.html'
    slug_field = 'username'      # Userモデルのusernameを使う
    slug_url_kwarg = 'username'  # URLの <str:username> と一致させる

    def get_object(self, queryset=None):
        user = super().get_object(queryset)
        # Profile がなければ作成
        Profile.objects.get_or_create(user=user)
        return user

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile_update.html'

    def get_object(self, queryset=None):
        # ログイン中ユーザーのプロフィール、なければ自動作成
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile
    
    def get_success_url(self):
        return reverse('accounts:profile_detail', kwargs={'username': self.request.user.username})

class FollowToggleView(LoginRequiredMixin, View):
    def post(self, request, username):
        target_user = get_object_or_404(User, username=username)
        target_profile = get_object_or_404(Profile, user=target_user)

        if request.user in target_profile.followers.all():
            # すでにフォローしていれば解除
            target_profile.followers.remove(request.user)
        else:
            # フォロー追加
            target_profile.followers.add(request.user)
            # 通知作成
            Notification.objects.create(
                sender=request.user,
                recipient=target_user,
                notification_type='follow',
            )
        return redirect('accounts:profile_detail', username=username)


