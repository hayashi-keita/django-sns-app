from django.shortcuts import render
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import SignupForm

class SignupView(CreateView):
    model = User
    template_name = 'accounts/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('sns:index')
