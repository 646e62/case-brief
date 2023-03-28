from django import forms
from .models import Analysis

class AnalysisForm(forms.ModelForm):
    output = forms.CharField(widget=forms.Textarea(attrs={'readonly': True}), required=False)

    class Meta:
        model = Analysis
        fields = ['facts', 'issues', 'rules', 'analysis', 'conclusion']
