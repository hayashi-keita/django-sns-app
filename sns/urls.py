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
    path('post/<int:pk>/like/', views.PostLikeView.as_view(), name='post_like'),
    path('message/create/', views.MessageCreateView.as_view(), name='message_create'),
    path('message/inbox/', views.MessageInboxView.as_view(), name='message_inbox'),
    path('message/outbox/', views.MessageOutboxView.as_view(), name='message_outbox'),
    path('message/<int:pk>/detail/', views.MessageDetailView.as_view(), name='message_detail'),
    path('message/<int:pk>/reply/', views.MessageReplyView.as_view(), name='message_reply'),
    path('message/<int:pk>/forward/', views.MessageForwardView.as_view(), name='message_forward'),
    path('message/<int:pk>/update/', views.MessageUpdateView.as_view(), name='message_update'),
    path('message/<int:pk>/delete/', views.MessageDeleteView.as_view(), name='message_delete'),
    path('attachment/<int:pk>/delete/', views.AttachmentDeleteView.as_view(), name='attachment_delete'),
    path('comment/<int:pk>/create/', views.CommentCreateView.as_view(), name='comment_create'),
    path('comment/<int:pk>/update/', views.CommentUpdateView.as_view(), name='comment_update'),
    path('comment/<int:pk>/delete', views.CommentDeleteView.as_view(), name='comment_delete'),
    path('comment/<int:pk>/like/', views.CommentLikeView.as_view(), name='comment_like'),
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notification/<int:pk>/read/', views.NotificationMarkReadView.as_view(), name='notification_mark_read'),
    path('notification/<int:pk>/delete/', views.NotificatonDeleteView.as_view(), name='notification_delete'),
]