import click
import pyarrow.parquet as pq

from singlecell.models import Annotation, Dataset
from django.core.management.base import BaseCommand, CommandError, CommandParser
from tqdm import tqdm


class Command(BaseCommand):
    help = "Import segmentations into the annotation app database."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('dataset', type=int)
        parser.add_argument('segmentations', type=str)

    def handle(self, *args, segmentations, dataset):

        try:
            dataset = Dataset.objects.get(pk=dataset)
        except Dataset.DoesNotExist:
            raise CommandError(f"Dataset {dataset} does not exist.")

        df = pq.read_table(segmentations).to_pandas()

        for idx, r in tqdm(df.itertuples(), file=self.stdout):
            ann = Annotation(
                dataset=dataset,
                segmentation_id=idx,
                scene=r.meta_scene,
                tile=r.meta_tile,
                bbox=",".join([r.bbox_minr, r.bbox_minc, r.bbox_maxr, r.bbox_maxc])
            )
            ann.save()
