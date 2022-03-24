from django import forms
from . import models
from django.conf import settings

LabelFormSet = forms.modelformset_factory(
    fields = ["label", "annotation"],
    model=models.Label,
    widgets={
        "label": forms.RadioSelect(),
        "annotation": forms.HiddenInput()
    },
    extra=settings.NUM_PER_SET
)