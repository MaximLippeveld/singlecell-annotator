from django.shortcuts import render
from django.http import HttpResponse
import base64
from django.contrib.staticfiles import finders

def index(request):

    # load the default dataset
    

    # find next unlabeled segmentation in the dataset

    # load image and load patch

    test_image = finders.find("test.jpg")
    with open(test_image, "rb") as img_file:
        patch_byte_str = base64.b64encode(img_file.read()).decode('UTF-8')

    return render(request, "singlecell/index.html", {"patch_byte_str": patch_byte_str})
