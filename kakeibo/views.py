from calendar import month
import json
from os import replace
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        qs = Record.objects.filter(user=self.request.user).values('date', 'category', 'amount')
        df = pd.DataFrame(qs)
        if not df.empty:
            # 月単位に変換
            df['month'] = pd.to_datetime(df['date']).dt.to_period('M').dt.to_timestamp()
            # カテゴリを日本語に変換
            category_map = dict(Record.CATEGORY_CHOICES)
            df['category'] = df['category'].map(category_map)
            # 月ごとに集計
            monthly = df.groupby(['month', 'category'])['amount'].sum().reset_index()
            monthly_pivot = monthly.pivot(index='month', columns='category', values='amount').fillna(0)
            # 収支を追加
            monthly_pivot['収支'] = monthly_pivot.get('収入', 0) - monthly_pivot.get('支出', 0)
            # インデックスをリセットして辞書化
            monthly_pivot.reset_index(inplace=True)
            context['monthly_table'] = monthly_pivot.to_dict(orient='records')
        else:
            context['monthly_table'] = []
        
        return context

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
        return reverse('kakeibo:record_detail', kwargs={'pk': self.object.pk})

class RecordDeleteView(LoginRequiredMixin, DeleteView):
    model = Record
    template_name = 'kakeibo/record_delete.html'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj
    
    def get_success_url(self):
        return reverse('kakeibo:record_detail', kwargs={'pk': self.object.pk})

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
        qs = Record.objects.filter(user=self.request.user).values('date', 'category', 'amount', 'memo')
        df = pd.DataFrame(qs)
        if df.empty:
            context['line_graph'] = None
            context['bar_graph'] = None
            context['pie_graph'] = None
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

        # ========= 折れ線グラフ =========
        fig_line = px.line(
            monthly_pivot,
            x='month',
            y=['収入', '支出', '収支'],
            title='📈 月ごとの収入・支出・収支',
            markers=True,
        )
        # 軸とフォーマットの調整
        fig_line.update_layout(xaxis_title='月', yaxis_title='金額（円）', legend_title='区分')
        fig_line.update_xaxes(tickformat='%Y-%m')
        fig_line.update_yaxes(tickprefix='¥', tickformat=',d')
        # HTMLとして埋め込む
        context['line_graph'] = fig_line.to_html(full_html=False)

        # ========= 棒グラフ =========
        fig_bar = px.bar(
            monthly,
            x='month',
            y='amount',
            color='category',
            barmode='group',
            title='📊 月ごとの収入・支出（棒グラフ）',
        )
        fig_bar.update_layout(xaxis_title='月', yaxis_title='金額（円）', legend_title='区分')
        fig_bar.update_xaxes(tickformat='%Y-%m')
        fig_bar.update_yaxes(tickprefix='￥', tickformat=',d')

        context['bar_graph'] = fig_bar.to_html(full_html=False)

        # ===== 支出割合 円グラフ =====
        expense_df = df[df['category'] == 'expense'].copy()
        if not expense_df.empty:
            # memo が空欄や None の場合は「未分類」に置き換え
            expense_df['memo'] = expense_df['memo'].fillna('未分類').replace('', '未分類')
            # メモ単位で集計
            expense_summary = expense_df.groupby('memo')['amount'].sum().reset_index()
            
            fig_pie = px.pie(
                expense_summary,
                names='memo',
                values='amount',
                title='🥧 支出の内訳（円グラフ）',
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            context['pie_graph'] = fig_pie.to_html(full_html=False)
        else:
            context['pie_graph'] = None

        return context

class RecordGraphChartJSView(LoginRequiredMixin, TemplateView):
    template_name = 'kakeibo/record_graph_chartjs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ログインユーザーの記録を取得
        qs = Record.objects.filter(user=self.request.user).values('date', 'category', 'amount', 'memo')
        df = pd.DataFrame(qs)

        if df.empty:
            context['chart_data'] = None
            return context
        # 日付を月単位に変換し、カテゴリを日本語に変換
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M').dt.to_timestamp()
        category_map = dict(Record.CATEGORY_CHOICES)
        df['category'] = df['category'].map(category_map)
        # 月ごとの収入・支出を集計
        monthly = df.groupby(['month', 'category'])['amount'].sum().reset_index()
        monthly_pivot = monthly.pivot(index='month', columns='category', values='amount').fillna(0)
        monthly_pivot['収支'] = monthly_pivot.get('収入', 0) - monthly_pivot.get('支出', 0)
        monthly_pivot.reset_index(inplace=True)
        # 棒、折れ線グラフ用データ
        chart_data = {
            'labels': monthly_pivot['month'].dt.strftime('%Y-%m').tolist(),
            'income': monthly_pivot.get('収入', pd.Series([0]*len(monthly_pivot))).tolist(),
            'expense': monthly_pivot.get('支出', pd.Series([0]*len(monthly_pivot))).tolist(),
            'balance': monthly_pivot['収支'].tolist(),
        }
        # 円グラフ用データ
        expense_df = df[df['category'] == '支出'].copy()
        if not expense_df.empty:
            expense_df['memo'] = expense_df['memo'].fillna('未分類').replace('', '未分類')
            expense_summary = expense_df.groupby('memo')['amount'].sum().reset_index()
            chart_data['expense_labels'] = expense_summary['memo'].to_list()
            chart_data['expense_values'] = expense_summary['amount'].to_list()
        else:
            chart_data['expense_labels'] = []
            chart_data['expense_values'] = []
        
        context['chart_data'] = json.dumps(chart_data)
        return context