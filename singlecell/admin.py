from django.contrib import admin
from singlecell.models import Dataset

# Register your models here.
class DatasetAdmin(admin.ModelAdmin):
    pass
admin.site.register(Dataset, DatasetAdmin)
