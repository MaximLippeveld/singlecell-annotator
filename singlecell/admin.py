from django.contrib import admin
from singlecell.models import Dataset, Annotation, Label

# Register your models here.
class DatasetAdmin(admin.ModelAdmin):
    pass
admin.site.register(Dataset, DatasetAdmin)

class AnnotationAdmin(admin.ModelAdmin):
    pass
admin.site.register(Annotation, AnnotationAdmin)

class LabelAdmin(admin.ModelAdmin):
    pass
admin.site.register(Label, LabelAdmin)
