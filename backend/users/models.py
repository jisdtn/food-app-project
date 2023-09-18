from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()

class Favorite(models.Model):
	objects = models.Manager()
	pass

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

