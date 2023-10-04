from django.contrib.auth import get_user_model
from django.db import models

from recipes.models import Recipe

User = get_user_model()

class Favorite(models.Model):
	objects = models.Manager()
	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='favored_by',
		verbose_name='Пользователь'
	)
	recipe = models.ForeignKey(
		Recipe,
		on_delete=models.CASCADE,
		related_name='favorite_recipe',
		verbose_name='Рецепт'
	)
	date_added = models.DateTimeField(
		auto_now_add=True,
		null=True,
		blank=True,
		verbose_name='Дата добавления',
	)

	class Meta:
		verbose_name = 'Избранное'
		verbose_name_plural = 'Избранное'
		constraints = [
			models.UniqueConstraint(
				fields=['user', 'recipe'], name='favorite_user_recept_unique'
			)
		]

	def __str__(self):
		return f'Рецепт "{self.recipe}" в избранном у {self.user}'


class Follow(models.Model):
	objects = models.Manager()
	user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
)
	following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
)

	class Meta:
		constraints = (models.UniqueConstraint(
            fields=['user', 'following'], name='unique_follower'),
        )

class ShoppingCart(models.Model):
	pass