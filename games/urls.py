from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    path('janken/', views.JankenView.as_view(), name='janken'),
]