from django.shortcuts import render
from django.db import models
from django.conf import settings
import base64
from PIL import Image
import numpy
import io
from singlecell.models import Annotation, Dataset
from singlecell import forms
from aicsimageio import AICSImage
import pandas


def get_next_images(dataset, n=3):

    number_labeled = dataset.annotation_set.filter(
        ~models.Q(label=Annotation.LabelChoices.NOT_SET)).count()
    total_patches = dataset.annotation_set.count()
    annotations = dataset.annotation_set.filter(label=Annotation.LabelChoices.NOT_SET)

    scenes = annotations.values("scene").annotate(total=models.Count("scene")).order_by("total")
    selected_scenes = []
    i = 0
    n2 = n
    while(n2 > 0):
        c = annotations.filter(scene=scenes[i]["scene"]).count()
        if c > 0:
            selected_scenes.append(scenes[i]["scene"])
            n2 -= c

    selected_annotations = annotations.filter(scene__in=selected_scenes).order_by("seg_id")[:n]

    # for performance reasons data has to be loaded per scene
    patches = []
    df = pandas.DataFrame(selected_annotations.values())
    for scene, a in df.groupby("scene"):
        if len(a) == 0:
            continue

        image = AICSImage(dataset.path, reconstruct_mosaic=False)
        image.set_scene(scene)

        for _, ann in a.iterrows():
            bbox = [int(float(x)) for x in ann.bbox.split(",")]
            pixels = image.get_image_data(
                "CZXY", T=0, M=ann.tile
            )[:, :, bbox[0]:bbox[2], bbox[1]:bbox[3]]
            pixels = numpy.max(pixels, axis=1)

            patch = {}
            for name, channel in zip(dataset.channel_names.split(","), pixels):
                channel = Image.fromarray(channel.astype('uint16'))
                in_mem_file = io.BytesIO()
                channel.save(in_mem_file, format = "PNG")
                in_mem_file.seek(0)

                patch[name] = base64.b64encode(in_mem_file.read()).decode('ascii')

            patches.append(patch)

    return selected_annotations, patches, number_labeled, total_patches


def index(request):

    formset = None

    if request.method == "POST":
        # save annotation to database
        formset = forms.AnnotationFormSet(
            request.POST
        )

        if formset.is_valid():
            formset.save()

    dataset = Dataset.objects.get()

    selected_annotations, patches, number_labeled, total_patches = get_next_images(
        dataset, n=settings.NUM_PER_SET)

    # create new form
    formset = forms.AnnotationFormSet(
        queryset=selected_annotations
    )

    context = {
        "formset": formset,
        "data": zip(formset.forms, patches),
        "dataset_name": dataset.name,
        "number_labeled": number_labeled,
        "total_patches": total_patches,
        "percent_labeled": "%.2f" % ((number_labeled/total_patches)*100)
    }

    return render(request, "singlecell/index.html", context)
