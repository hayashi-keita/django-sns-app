from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views


app_name = 'accounts'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path ('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('profiles/', views.ProfileListView.as_view(), name='profile_list'),
    path('profile/<str:username>/detail', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('follow/<str:username>/', views.FollowToggleView.as_view(), name='follow_toggle'),
]