from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('event/<int:pk>/update/', views.EventUpdateView.as_view(), name='event_update'),
    path('event/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    path('event/<int:pk>/detail/', views.EventDetailView.as_view(), name='event_detail'),
]