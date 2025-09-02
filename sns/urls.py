from django.urls import path
from . import views

app_name = 'sns'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('posts/', views.PostListView.as_view(), name='post_list'),
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/detail/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('message/create/', views.MessageCreateView.as_view(), name='message_create'),
    path('message/inbox/', views.MessageInboxView.as_view(), name='message_inbox'),
    path('message/outbox/', views.MessageOutboxView.as_view(), name='message_outbox'),
    path('message/<int:pk>/detail/', views.MessageDetailView.as_view(), name='message_detail'),
    path('message/<int:pk>/reply/', views.MessageReplyView.as_view(), name='message_reply'),
    path('message/<int:pk>/forward/', views.MessageForwardView.as_view(), name='message_forward'),
]