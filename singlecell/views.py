from django.shortcuts import render
from django.db import models
from django.conf import settings
import base64
from PIL import Image
import numpy
import io
from singlecell.models import Label, Dataset
from singlecell import forms
from aicsimageio import AICSImage
import pandas


def get_next_images(dataset, n=3):

    if dataset.indices == "":
        channel_indices = numpy.s_[:]
    else:
        channel_indices = [int(x) for x in dataset.indices.split(",")]

    total_patches = dataset.annotation_set.count()

    annotations = dataset.annotation_set.annotate(models.Count("label"))
    number_labeled = annotations.filter(label__count__gt=0).count()
    empty_annotations = annotations.filter(label__count=0)

    scenes, counts = numpy.unique(
        [v["scene"] for v in empty_annotations.values("scene")], return_counts=True)

    selected_scenes = []
    random_idx = numpy.random.choice(len(scenes), size=len(scenes), replace=False)
    t = 0
    for c in random_idx:
        t += counts[c]
        selected_scenes.append(scenes[c])
        if t > n:
            break

    selected_annotations = empty_annotations.filter(
        scene__in=selected_scenes).order_by("seg_id")[:n]

    # for performance reasons data has to be loaded per scene
    patches = []
    stacks = []
    df = pandas.DataFrame(selected_annotations.values())
    for scene, a in df.groupby("scene"):
        if len(a) == 0:
            continue

        image = AICSImage(dataset.path, reconstruct_mosaic=False)
        image.set_scene(scene)

        for _, ann in a.iterrows():
            bbox = [int(float(x)) for x in ann.bbox.split(",")]
            tmp = image.get_image_data(
                "CZXY", T=0, M=ann.tile
            )[channel_indices, :, bbox[0]:bbox[2], bbox[1]:bbox[3]]

            pixels = numpy.empty(shape=(tmp.shape[0], tmp.shape[2], tmp.shape[3]), dtype=tmp.dtype)
            pixels[0] = tmp[0, 0]
            pixels[1:] = numpy.max(tmp[1:], axis=1)

            patch = {}
            for name, channel in zip(dataset.channel_names.split(","), pixels):
                channel = (channel - channel.min()) / (channel.max() - channel.min())
                channel *= numpy.iinfo("uint16").max
                channel = Image.fromarray(channel.astype('uint16'))
                in_mem_file = io.BytesIO()
                channel.save(in_mem_file, format = "PNG")
                in_mem_file.seek(0)

                patch[name] = base64.b64encode(in_mem_file.read()).decode('ascii')

            stack = []
            for plane in tmp[0, 1:]:
                plane = (plane - plane.min()) / (plane.max() - plane.min())
                plane *= numpy.iinfo("uint16").max
                plane = Image.fromarray(plane.astype('uint16'))
                in_mem_file = io.BytesIO()
                plane.save(in_mem_file, format = "PNG")
                in_mem_file.seek(0)

                stack.append(base64.b64encode(in_mem_file.read()).decode('ascii'))

            patches.append(patch)
            stacks.append(stack)

    return selected_annotations, patches, stacks, number_labeled, total_patches


def index(request):

    formset = None

    if request.method == "POST":
        # save annotation to database
        formset = forms.LabelFormSet(
            request.POST
        )

        if formset.is_valid():
            formset.save()

    dataset = Dataset.objects.get()

    selected_annotations, patches, stacks, number_labeled, total_patches = get_next_images(
        dataset, n=settings.NUM_PER_SET)

    # create new form
    formset = forms.LabelFormSet(initial=[
        {'annotation': annotation}
        for annotation in selected_annotations
    ],
        queryset=Label.objects.none()
    )

    context = {
        "formset": formset,
        "data": zip(formset.forms, patches, stacks),
        "dataset_name": dataset.name,
        "number_labeled": number_labeled,
        "total_patches": total_patches,
        "percent_labeled": "%.2f" % ((number_labeled/total_patches)*100)
    }

    return render(request, "singlecell/index.html", context)
