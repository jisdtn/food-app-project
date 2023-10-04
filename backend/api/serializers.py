from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import MultipleChoiceField
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserCreateSerializer

from recipes.models import Recipe, Tag, Ingredient, IngredientInRecipe
from users.models import Follow

User = get_user_model()

# Согласно спецификации, обновление рецептов должно быть реализовано через PUT,
# значит, при редактировании все поля модели рецепта должны полностью перезаписываться.
# Используйте подходящие типы related-полей;
# для некоторых данных вам потребуется использовать SerializerMethodField.
# При публикации рецепта фронтенд кодирует картинку в строку base64;
# на бэкенде её необходимо декодировать и сохранить как файл.
# Для этого будет удобно создать кастомный тип поля для картинки, переопределив метод сериализатора to_internal_value.
class IngredientSerializer(serializers.ModelSerializer):
	ingredient_name = serializers.CharField(source='name')

	class Meta:
		model = Ingredient
		fields = (
			'id',
			'name',
			'measurement_unit',
		)


# Для сохранения ингредиентов и тегов рецепта потребуется переопределить методы create и update в ModelSerializer.

class RecipeSerializer(serializers.ModelSerializer):
	ingredients = IngredientSerializer(many=True)
	author = serializers.SlugRelatedField(
		slug_field='username',
		read_only=True
	)
	class Meta:
		model = Recipe
		fields = ('id', 'author', 'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time')

	def create(self, validated_data):
		if 'ingredients' and 'tags' not in self.initial_data:
			recipe = Recipe.objects.create(**validated_data)
			return recipe
		ingredients = validated_data.pop('ingredients')
		recipe = Recipe.objects.create(**validated_data)
		for ingredient in ingredients:
			current_ingredient, status = Ingredient.objects.get_or_create(
				**ingredient
			)
			IngredientInRecipe.objects.create(
				ingredient=current_ingredient, recipe=recipe
			)
		return recipe

	def update(self, instance, validated_data):
		instance.name = validated_data.get('name', instance.name)
		instance.text = validated_data.get('text', instance.text)
		instance.cooking_time = validated_data.get(
			'cooking_time', instance.cooking_time
		)
		instance.image = validated_data.get('image', instance.image)

		if 'ingredients' and 'tags' not in validated_data:
			instance.save()
			return instance

		ingredients_data = validated_data.pop('ingredients')
		tags_data = validated_data.pop('tags')
		lst = []
		for ingredient in ingredients_data:
			current_ingredient, status = Ingredient.objects.get_or_create(
				**ingredient
			)
			lst.append(current_ingredient)
		instance.ingredients.set(lst)

		instance.save()
		return instance

# class IngredientInRecipeSerializer(serializers.ModelSerializer):
# 	pass
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
		fields = ('id', 'name', 'color', 'slug')


class UserListSerializer(serializers.ModelSerializer):
	class Meta:
		model = User

class ProfileSerializer(UserCreateSerializer):
	is_subscribed = serializers.SerializerMethodField(read_only=True)
	class Meta:
		model = User
		fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed ')
