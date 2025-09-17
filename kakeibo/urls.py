from django.urls import path
from . import views

app_name = 'kakeibo'

urlpatterns = [
    path('records/', views.RecordListView.as_view(), name='record_list'),
    path('record/create/', views.RecordCreateView.as_view(), name='record_create'),
    path('record/<int:pk>/update/', views.RecordUpdateView.as_view(), name='record_update'),
    path('record/<int:pk>/delete/', views.RecordDeleteView.as_view(), name='record_delete'),
    path('record/<int:pk>/detail/', views.RecordDetailView.as_view(), name='record_detail'),
    path('record/graph/', views.RecordGraphView.as_view(), name='record_graph'),
    path('record/graph_chartjs/', views.RecordGraphChartJSView.as_view(), name='record_graph_chartjs'),
]