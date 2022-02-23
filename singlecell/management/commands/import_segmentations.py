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
        parser.add_argument('--limit', type=int, default=-1)

    def handle(self, *args, segmentations, dataset, limit, **options):

        try:
            dataset = Dataset.objects.get(pk=dataset)
        except Dataset.DoesNotExist:
            raise CommandError(f"Dataset {dataset} does not exist.")

        df = pq.read_table(segmentations).to_pandas()

        if limit > 0:
            df = df.sample(n=limit)

        for idx, r in tqdm(df.iterrows(), file=self.stdout, total=len(df)):
            ann = Annotation(
                dataset=dataset,
                seg_id=idx,
                scene=r.meta_scene,
                tile=r.meta_tile,
                bbox=",".join(
                    str(x)
                    for x in
                    [r.meta_bbox_minr, r.meta_bbox_minc, r.meta_bbox_maxr, r.meta_bbox_maxc])
            )
            ann.save()
