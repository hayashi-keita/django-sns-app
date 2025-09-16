from django import forms
from .models import Record

class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['date', 'category', 'amount', 'memo']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }