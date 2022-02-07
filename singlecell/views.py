from django.shortcuts import render
from django.http import HttpResponse
from . import models
from . import forms
import base64
from django.contrib.staticfiles import finders
from c7m import load_tiff_images, process_segmentation
from PIL import Image
import pandas
import numpy
import io
import os


def read_tiff(path):
    """
    path - Path to the multipage-tiff file
    """
    with Image.open(path) as img:
        images = []
        for i in range(img.n_frames):
            img.seek(i)
            images.append(numpy.array(img))
        return numpy.array(images)

names = ["DAPI", "eGFP (CD45)", "RPe (Siglec 8)", "APC (CD15)", "BF", "Oblique 1", "Oblique 2"]

def get_next_images(dataset, n=3):

    # find next unlabeled segmentation in the dataset
    segmentations = pandas.read_csv(dataset.segmentations, index_col=0)
    sel = segmentations["CD15+"]

    segmentations["labeled"] = False

    all_annotations = dataset.annotation_set.all()
    for a in all_annotations:
        segmentations.loc[a.seg_id, "labeled"] = True

    number_labeled = all_annotations.count()
    total_patches = segmentations[sel].shape[0]

    s = segmentations[sel & ~segmentations["labeled"]].groupby("series")["labeled"].sum()
    s = s.sort_values(ascending=False).index

    series = s[:n]

    seg_ids, patches = [], []
    for serie in series:
        seg_id = segmentations[
            sel
            & (segmentations["series"]==serie)
            & ~segmentations["labeled"]
        ].index[0]
        seg_ids.append(seg_id)

        patch = get_next_image(serie, dataset.path, segmentations.loc[seg_id])
        patches.append(patch)

    return series.values.tolist(), seg_ids, patches, number_labeled, total_patches


def get_next_image(series, path, segmentation):

    patch = {}

    image = read_tiff(os.path.join(path, f"series_{series}.ome.tiff"))

    for channel, name in enumerate(names):
        z_stack = []

        for z in range(1):
            # load image and load patch
            z_slice = image[channel + z*len(names)]

            p = process_segmentation.extract_patch_from_image(segmentation[:4], z_slice)
            p = ((p-numpy.min(p))/(numpy.max(p)-numpy.min(p)))*65535
            p = Image.fromarray(p.astype('uint16'))

            in_mem_file = io.BytesIO()
            p.save(in_mem_file, format = "PNG")
            in_mem_file.seek(0)

            z_stack.append(
                base64.b64encode(in_mem_file.read()).decode('ascii')
            )

        patch[name] = z_stack

    return patch


def index(request):

    formset = None

    if request.method == "POST":
        # save annotation to database
        formset = forms.AnnotationFormSet(request.POST)

        if formset.is_valid():
            formset.save()

    # load the default dataset
    dataset = models.Dataset.objects.get()

    # show next image
    series, seg_ids, patches, number_labeled, total_patches = get_next_images(dataset, n=3)

    # create new form
    formset = forms.AnnotationFormSet()

    context = {
        "formset": formset,
        "data": zip(formset.forms, patches, series, seg_ids),
        "dataset_name": dataset.name,
        "number_labeled": number_labeled,
        "total_patches": total_patches,
        "percent_labeled": "%.2f" % ((number_labeled/total_patches)*100)
    }

    return render(request, "singlecell/index.html", context)
