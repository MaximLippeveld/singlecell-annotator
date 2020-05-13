from django.db import models


class Dataset(models.Model):
    name = models.CharField("Name of the dataset", "name", max_length=255)
    data_path = models.CharField("Path to the dataset", "path", max_length=1024)
    segmentations_path = models.CharField("Path to the segmentations", "segmentations", max_length=1024)

    def __str__(self):
        return self.name


class Annotation(models.Model):

    class Meta:
        unique_together = ('dataset', 'seg_id')

    class LabelChoices(models.IntegerChoices):
        BAD_SEGMENT = 0, "Bad segmentation"
        ONELOBE = 1, "1 lobe"
        TWOLOBES = 2, "2 lobes"
        THREELOBES = 3, "3 lobes"
        FOURLOBES = 4, "4 lobes"
        UNCLEAR = 5, "Unclear amount of lobes"

    label = models.IntegerField("Label assigned in this annotation", "label", choices=LabelChoices.choices, default=LabelChoices.UNCLEAR)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    segmentation_id = models.IntegerField("Index of segmentation to which this annotation is linked", "seg_id")

    def __str__(self):
        return f"Annotation for segmentation {self.seg_id} in {self.dataset.name}"
