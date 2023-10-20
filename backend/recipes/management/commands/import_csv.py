import csv

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):

        with open(
            f'{settings.BASE_DIR}/../data/ingredients.csv',
            'r', encoding='utf-8'
        ) as csv_file:
            reader = csv.reader(csv_file)
            result = Ingredient.objects.bulk_create(
                Ingredient(name=data[0], measurement_unit=data[1])
                for data in reader)

        self.stdout.write("success, inserted: " + str(len(result)))
