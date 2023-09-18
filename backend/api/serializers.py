from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Recipe, Tag
from users.models import Follow, User


class IngredientSerializer:
	pass


class RecipeSerializer(serializers.ModelSerializer):
	# ingredients = IngredientSerializer(many=True, required=True)
	author = serializers.SlugRelatedField(
		slug_field='username',
		read_only=True
	)
	class Meta:
		model = Recipe
		fields = ('author', 'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time')

	def clean_text(self, value):
		value = self.text
		if value == " ":
			raise serializers.ValidationError("Рецепт не может быть пустым")
		return value


class FollowSerializer(serializers.ModelSerializer):
	user = serializers.SlugRelatedField(
		slug_field='username',
		read_only=True,
		default=serializers.CurrentUserDefault()
	)

	following = serializers.SlugRelatedField(
		slug_field='username',
		queryset=User.objects.all()
	)

	class Meta:
		model = Follow
		fields = '__all__'
		validators = [
			UniqueTogetherValidator(
				queryset=Follow.objects.all(),
				fields=['user', 'following'],
				message='You are already subscribed'
			)
		]

	def validate_following(self, value):
		if self.context['request'].user == value:
			raise serializers.ValidationError(
				'You can not follow yourself'
			)
		return value


class TagSerializer(serializers.ModelSerializer):
	# color = Hex2NameColor()
	class Meta:
		model = Tag
		fields = ('name', 'color', 'slug')


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
