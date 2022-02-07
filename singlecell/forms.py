from django import forms
from . import models

AnnotationFormSet = forms.modelformset_factory(
    fields = "__all__",
    model = models.Annotation,
    widgets = {
        'seg_id': forms.HiddenInput(),
        'dataset': forms.HiddenInput()
    },
    extra=3
)