from django.shortcuts import render
from django.views.generic import (
    ListView, CreateView, UpdateView,
    DeleteView, DetailView, TemplateView,
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from .models import Record
from .forms import RecordForm
import plotly.express as px
import pandas as pd
from plotly.offline import plot

class RecordListView(LoginRequiredMixin, ListView):
    model = Record
    template_name = 'kakeibo/record_list.html'

    def get_queryset(self):
        return Record.objects.filter(user=self.request.user).order_by('-date')

class RecordCreateView(LoginRequiredMixin, CreateView):
    model = Record
    template_name = 'kakeibo/record_create.html'
    form_class = RecordForm
    success_url = reverse_lazy('kakeibo:record_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class RecordUpdateView(LoginRequiredMixin, UpdateView):
    model = Record
    template_name = 'kakeibo/record_update.html'
    form_class = RecordForm

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

    def get_success_url(self):
        return reverse('kakeibo:record_list', kwargs={'pk': self.object.pk})

class RecordDeleteView(LoginRequiredMixin, DeleteView):
    model = Record
    template_name = 'kakeibo/record_delete.html'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj
    
    def get_success_url(self):
        return reverse('kakeibo:record_list', kwargs={'pk': self.object.pk})

class RecordDetailView(LoginRequiredMixin, DetailView):
    model = Record
    template_name= 'kakeibo/record_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

class RecordGraphView(LoginRequiredMixin, TemplateView):
    template_name = 'kakeibo/record_graph.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ユーザーの記録を取得してデータフレーム作成
        qs = Record.objects.filter(user=self.request.user).values('date', 'category', 'amount')
        df = pd.DataFrame(qs)
        if df.empty:
            context['graph'] = None
            return context
        # 月ごとの集計
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M').dt.to_timestamp()
        monthly = df.groupby(['month', 'category'])['amount'].sum().reset_index()
        # カテゴリを日本語に変換
        category_map = dict(Record.CATEGORY_CHOICES)
        monthly['category'] = monthly['category'].map(category_map)
        # 収入/支出を列に展開
        monthly_pivot = monthly.pivot(index='month', columns='category', values='amount').fillna(0)
        # 収支を追加
        monthly_pivot['収支'] = monthly_pivot.get('収入', 0) - monthly_pivot.get('支出', 0)
        # Indexをリセット
        monthly_pivot.reset_index(inplace=True)
        #折れ線グラフ作成
        fig = px.line(
            monthly_pivot,
            x='month',
            y=['収入', '支出', '収支'],
            title='月ごとの収入・支出・収支',
            markers=True,
        )
        # 軸とフォーマットの調整
        fig.update_layout(xaxis_title='月', yaxis_title='金額（円）', legend_title='区分')
        fig.update_xaxes(tickformat='%Y-%m')
        fig.update_yaxes(tickprefix='¥', separatethousands=True, tickformat='d')

        # HTMLとして埋め込む
        context['graph'] = fig.to_html(full_html=False)
        return context