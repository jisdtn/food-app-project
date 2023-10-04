from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models


User = get_user_model()

class Ingredient(models.Model):
	objects = models.Manager()
	name = models.CharField(max_length=200, db_index=True)
	measurement_unit = models.TextField()

	class Meta:
		unique_together = ('name', 'measurement_unit')
		ordering = ('name', )

	def __str__(self):
		return self.name


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
		through='IngredientInRecipe')

	tags = models.ForeignKey(
		Tag, on_delete=models.SET_NULL,
        related_name='recipes', blank=True, null=True)
	image = models.ImageField(
		upload_to='recipes/images', null=True, blank=True)
	name = models.CharField(max_length=200)
	text = models.TextField()
	cooking_time = models.IntegerField(validators=[MinValueValidator(1)])
	pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

	class Meta:
		ordering = ('-pub_date',)
		constraints = [
			models.UniqueConstraint(
				fields=['name', 'author'],
				name='recipe_unique'
			)
		]

	def __str__(self):
		return self.name

class IngredientInRecipe(models.Model):
	objects = models.Manager()
	ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
	amount = models.PositiveIntegerField(
		validators=[MinValueValidator(1)],

	)

	def __str__(self):
		return f'Ingredient "{self.ingredient}" for the "{self.recipe}" recipe'
