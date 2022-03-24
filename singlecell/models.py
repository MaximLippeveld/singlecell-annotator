from django.db import models
from django.core.validators import int_list_validator


class Dataset(models.Model):
    name = models.CharField("Name of the dataset", "name", max_length=255)
    data_path = models.CharField("Path to the dataset", "path", max_length=1024)
    segmentations_path = models.CharField(
        verbose_name="Path to the segmentations",
        name="segmentations",
        max_length=1024
    )
    channel_names = models.CharField(
        verbose_name="Comma-separated list of channel names",
        name="channel_names",
        max_length=255
    )
    channel_indices = models.CharField(
        verbose_name="Comma-separated list of channel indices",
        name="indices",
        max_length=255,
        validators=[int_list_validator],
        default=""
    )

    def __str__(self):
        return self.name


class Annotation(models.Model):

    class Meta:
        unique_together = ('dataset', 'seg_id')


    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    segmentation_id = models.IntegerField(
        verbose_name="Index of segmentation to which this annotation is linked",
        name="seg_id"
    )
    scene = models.CharField(
        verbose_name="CZI Scene",
        name="scene",
        max_length=255
    )
    tile = models.IntegerField(
        verbose_name="Tile within scene",
        name="tile"
    )
    bbox = models.CharField(
        verbose_name="min row, min column, max row, max column",
        name="bbox",
        validators=[int_list_validator],
        max_length=255
    )

    def __str__(self):
        return f"Annotation for segmentation {self.seg_id} in {self.dataset.name}"


class Label(models.Model):

    class Choices(models.IntegerChoices):
        BAD_SEGMENT = 0, "Bad segmentation"
        ONELOBE = 1, "1 lobe"
        TWOLOBES = 2, "2 lobes"
        THREELOBES = 3, "3 lobes"
        FOURLOBES = 4, "4 lobes"
        FIVELOBES = 5, "5 lobes",
        UNCLEAR = 6, "Unclear amount of lobes"

    label = models.IntegerField(
        verbose_name="Label",
        name="label",
        choices=Choices.choices,
    )
    annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE)
