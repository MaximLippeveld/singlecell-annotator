from django.shortcuts import render
from django.http import HttpResponse
from . import models
from . import forms
import base64
from django.contrib.staticfiles import finders
from c7m import load_images, process_segmentation
from PIL import Image
import pandas
import numpy
import io
import os
import threading

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


def get_next_image(dataset):

    # find next unlabeled segmentation in the dataset
    segmentations = pandas.read_csv(dataset.segmentations, index_col=0)

    # only select CD15+ cells
    segmentations = segmentations[segmentations["CD15+"]]

    segmentations["labeled"] = False

    for a in dataset.annotation_set.all():
        segmentations.loc[a.seg_id, "labeled"] = True
    
    counts = {}
    for s_idx, df in segmentations.groupby("series"):
        counts[s_idx] = df["labeled"].sum()

    series = min(counts, key=counts.get)
    seg_id = segmentations[segmentations["series"]==series].index[0]

    segmentation = segmentations.loc[seg_id]
    
    patch = {}

    names = ["DAPI", "eGFP (CD45)", "RPe (Siglec 8)", "APC (CD15)", "BF", "Oblique 1", "Oblique 2"]

    image = read_tiff(os.path.join(dataset.path, f"series_{series}.ome.tiff"))
    
    for channel, name in enumerate(names):
        z_stack = []

        for z in range(3):
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

    return series, seg_id, patch



def index(request):

    form = None

    if request.method == "POST":
        # save annotation to database

        a = models.Annotation.objects.filter(
            seg_id=request.POST["seg_id"], 
            dataset__pk=request.POST["dataset"]
        ).first()
        form = forms.AnnotationForm(request.POST, instance=a)

        if form.is_valid():
            form.save()
        
    # load the default dataset
    dataset = models.Dataset.objects.get()

    # show next image
    series, seg_id, patch = get_next_image(dataset)
        
    # create new form
    form = forms.AnnotationForm(initial={
        "dataset": dataset.pk,
        "seg_id": seg_id
    })

    context = {
        "patch": patch,
        "form": form,
        "series": series,
        "patch_id": seg_id,
        "dataset_name": dataset.name
    }

    return render(request, "singlecell/index.html", context)
