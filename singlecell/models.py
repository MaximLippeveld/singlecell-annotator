from django.db import models

# Create your models here.
class Dataset(models.Model):
    name = models.CharField("Name of the dataset", "name", max_length=255)
    data_path = models.CharField("Path to the dataset", "path", max_length=1024)
    segmentations_path = models.CharField("Path to the segmentations", "segmentations", max_length=1024)

    def __str__(self):
        return self.name


class Annotation(models.Model):
    label = models.IntegerField("Label assigned in this annotation", "label")
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    segmentation_id = models.IntegerField("Index of segmentation to which this annotation is linked", "seg_id")
