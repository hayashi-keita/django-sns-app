from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View, DetailView
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Event
from .forms import EventForm

class DashboardView(LoginRequiredMixin, View):
    template_name = 'schedule/dashboard.html'
    
    def get(self, request):
        today = timezone.now().date()
        events = Event.objects.filter(
            user=request.user,
            start_time__year=today.year,
            start_time__month=today.month,
        ).order_by('start_time')
        form = EventForm()
        return render(request, self.template_name, {
            'form': form,
            'events': events,
            'today': today,
        })
    def post(self, request):
        today = timezone.now().date()
        events = Event.objects.filter(
            user=request.user,
            start_time__year=today.year,
            start_time__month=today.month,
        ).order_by('start_time')
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            return redirect('schedule:dashboard')
        
        return render(request, self.template_name, {
            'form': form,
            'events': events,
            'today': today,
        })

class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'schedule/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user).order_by('start_time')

class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    template_name = 'schedule/event_update.html'
    form_class = EventForm
    success_url = reverse_lazy('schedule:dashboard')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    template_name = 'schedule/event_delete.html'
    success_url = reverse_lazy('schedule:dashboard')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj
    
class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'schedule/event_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj