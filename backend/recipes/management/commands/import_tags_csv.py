import csv

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    pass
    # def handle(self, *args, **options):
    #
    #     INSERT INTO
    #         tags
    #
    #     ) as values:
    #         reader = reader(values)
    #         result = Tag.objects.bulk_create(Tag(name=data[0], measurement_unit=data[1]) for data in reader)
    #
    #     self.stdout.write("success, inserted: " + str(len(result)))
