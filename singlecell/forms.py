from django import forms
from . import models

class AnnotationForm(forms.ModelForm):
    class Meta:
        model = models.Annotation
        fields = '__all__'
        widgets = {
            'seg_id': forms.HiddenInput(),
            'dataset': forms.HiddenInput()
        }
