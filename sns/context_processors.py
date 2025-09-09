from .models import Message, Notification

# settings.pyのtemplatesに追加が必要
def unread_message_count(request):
    if request.user.is_authenticated:
        unread_count = Message.objects.filter(
            recipient=request.user,
            is_read=False,
        ).count()
        return {'unread_count': unread_count}
    
    return {'unread_count': 0}

def unread_notification_count(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).count()
        return {'unread_notification_count': unread_count}
    
    return {'unread_notification_count': 0}