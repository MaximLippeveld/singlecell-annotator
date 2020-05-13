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
import bioformats
import javabridge
import javabridge._javabridge as _jb
import os
import threading


def get_next_image(dataset):

    # find next unlabeled segmentation in the dataset
    segmentations = pandas.read_csv(dataset.segmentations)
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

    if not _jb.get_vm().is_active() or _jb.get_env() is None:
        javabridge.start_vm(class_path=bioformats.JARS)
    
    with bioformats.ImageReader(dataset.path) as reader:
        for channel, name in enumerate(names):
            z_stack = []

            for z in range(3):
                # load image and load patch
                z_slice = reader.read(c=channel, z=z, series=segmentation["series"])

                p = process_segmentation.extract_patch_from_image(segmentation[:4], z_slice)
                p = ((p-numpy.min(p))/(numpy.max(p)-numpy.min(p)))*255
                p = Image.fromarray(p.astype('uint8'))

                in_mem_file = io.BytesIO()
                p.save(in_mem_file, format = "JPEG")
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
