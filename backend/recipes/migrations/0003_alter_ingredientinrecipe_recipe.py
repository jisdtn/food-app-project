# Generated by Django 3.2.21 on 2023-10-20 09:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20231013_1352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredientinrecipe', to='recipes.recipe'),
        ),
    ]