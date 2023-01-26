# Single-cell annotator

![Annotation demo](annotation_demo.gif)

Single-cell anntator is a web app for manually annotating images of single-cells. It presents
the user with a number of randomly selected unlabaled cells in an easy-to-use interface.

The app is built using Django and TailwindCSS.

## Features
* Read images directly from Carl Zeiss Image (CZI) files
* Support for multiple annotations per cell
* Easy to configure thanks to Django administration
* Export annotations to CSV

# Installation

Download the repository tarball, untar, navigate in the directory and install using pip.
```
wget https://github.com/MaximLippeveld/singlecell-annotator/tarball/main -o main.tgz
tar xzf main.tgz
cd MaximLippeveld-singlecell-annotator*
pip install .
```

# Usage

## Serving the app

Set the environment variable `DJANGO_SETTINGS_MODULE` to
`annotator.settings.local` when developing, and to `annotator.settings.prod` when serving
the app publicly. In the latter case, you must also set the `DJANGO_SECRET_KEY` environment
variable to a random string.

There are two options to serve the webapp:
* Using the Django built-in development server
```
python manage.py runserver
```
This runs the app at port 8000 on the localhost.
* or, using `gunicorn`
```
gunicorn \
  --access-logfile - \
  --workers 3 \
  --env DJANGO_SETTINGS_MODULE=annotator.settings.prod \
  --env DJANGO_SECRET_KEY=secret_key \
  --bind unix:/run/gunicorn.sock \
  annotator.wsgi:application
```
This runs the app at the /run/gunicorn.sock socket, which can be served using a reverse proxy
like `nginx`.

Make sure the current working directory is set to where you untarred the repository
when launching these commands.

Set NUM_PER_SET in [production](annotator/settings/prod.py) or [local](annotator/settings/local.py)
settings to define the number of cells shown per page load.

## Managment commands

Import segmentations from Pandas dataframe:
```
python manage.py import_segmentations {dataset_id} {segmentations_file} [--limit {limit}]
```
Replace:
* `{dataset_id}` with the primary key of the dataset you created in the Django administator
* `{segmentations_file}` with a parquet-file containing a Pandas dataframe with columns:
  * meta_scene: scene id from CZI-file
  * meta_tile: tile id from CZI-file
  * meta_bbox_minr, meta_bbox_maxr, meta_bbox_minc, meta_bbox_maxc: bounding box coordinates
* `{limit}` with optional limit on the amount of rows to import

Export annotations to CSV using the following commands:
```
python manage.py {dataset_id} --path output.csv
```
Replace `{dataset_id}` with the dataset's primary key.

## Docker

To run the app set
the `DATA` environment variable to the root directory containing the
image file to be annotated, and the `DB` variable to the root directory
containing the `sqlite` database or where it should be created.

Then, in the repo directory, run
```
docker-compose up
```

The app is served on `localhost:8000`.

The management commands can also be used from the docker image.
Either use the image built by `docker-compose` or run
```
docker build .
```
Then run the command by running
```
docker run singlecell-annotator [command]
```
Replacing `[command]` with the management command you want to execute.
