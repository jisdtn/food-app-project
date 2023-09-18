from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
	name = models.CharField(max_length=200, unique=True)
	measurement_unit = models.CharField


class Tag(models.Model):
	objects = models.Manager()
	name = models.CharField(max_length=200, unique=True)
	color = models.CharField(max_length=16)
	slug = models.SlugField(unique=True)

	def __str__(self):
		return self.name


class Recipe(models.Model):
	objects = models.Manager()
	author = models.ForeignKey(
		User, on_delete=models.CASCADE, related_name='recipes')
	ingredients = models.ManyToManyField(
		Ingredient,
		related_name='recipes',
		verbose_name='Ингредиент')

	tags = models.ForeignKey(
		Tag, on_delete=models.SET_NULL,
        related_name='recipes', blank=True, null=True)
	image = models.ImageField(
		upload_to='recipes/', null=True, blank=True)
	name = models.CharField(max_length=200)
	text = models.TextField()
	cooking_time = models.TimeField(validators=[MinValueValidator(1)])

	def __str__(self):
		return self.name

