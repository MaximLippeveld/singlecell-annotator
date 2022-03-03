from django import forms
from . import models
from django.conf import settings

AnnotationFormSet = forms.modelformset_factory(
    fields = ["label", "seg_id", "dataset"],
    model = models.Annotation,
    widgets = {
        'seg_id': forms.HiddenInput(),
        'dataset': forms.HiddenInput(),
        'label': forms.RadioSelect()
    },
    max_num=settings.NUM_PER_SET
)