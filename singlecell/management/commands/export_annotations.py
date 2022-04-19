from singlecell.models import Label, Dataset
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import models
import pandas
from pathlib import Path
from datetime import datetime


class Command(BaseCommand):
    help = "Export annotations from the app database."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('dataset', type=int)
        parser.add_argument('--path', type=Path)

    def handle(self, *args, dataset, path, **options):

        try:
            dataset = Dataset.objects.get(pk=dataset)
        except Dataset.DoesNotExist:
            raise CommandError(f"Dataset {dataset} does not exist.")

        if path is None:
            path = Path("annotations_dataset%d_%s.csv" % (
                dataset.pk,
                datetime.now().strftime("%d%m%Y%H%M")
            ))

        df = pandas.DataFrame(
            Label.objects.filter(annotation__dataset=dataset).values("annotation__seg_id", "label"))
        df["label_name"] = df["label"].apply(lambda l: Label.Choices.names[l])

        df.to_csv(path, index=False)
