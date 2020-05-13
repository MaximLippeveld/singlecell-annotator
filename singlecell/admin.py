from django.contrib import admin
from singlecell.models import Dataset, Annotation

# Register your models here.
class DatasetAdmin(admin.ModelAdmin):
    pass
admin.site.register(Dataset, DatasetAdmin)

class AnnotationAdmin(admin.ModelAdmin):
    pass
admin.site.register(Annotation, AnnotationAdmin)
