from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    path('janken/', views.JankenView.as_view(), name='janken'),
    path('number_guess/', views.NumberGuessVeiw.as_view(), name='number_guess'),
    path('fortune_weather/', views.FortuneWeatherView.as_view(), name='fortune_weather')
]