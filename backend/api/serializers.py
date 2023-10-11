from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.fields import SerializerMethodField

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
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

	# def create(self, validated_data):
	# 	if 'ingredients' and 'tags' not in self.initial_data:
	# 		recipe = Recipe.objects.create(**validated_data)
	# 		return recipe
	# 	ingredients = validated_data.pop('ingredients')
	# 	recipe = Recipe.objects.create(**validated_data)
	# 	for ingredient in ingredients:
	# 		current_ingredient, status = Ingredient.objects.get_or_create(
	# 			**ingredient
	# 		)
	# 		IngredientInRecipe.objects.create(
	# 			ingredient=current_ingredient, recipe=recipe
	# 		)
	# 	return recipe
	#
	# def update(self, instance, validated_data):
	# 	instance.name = validated_data.get('name', instance.name)
	# 	instance.text = validated_data.get('text', instance.text)
	# 	instance.cooking_time = validated_data.get(
	# 		'cooking_time', instance.cooking_time
	# 	)
	# 	instance.image = validated_data.get('image', instance.image)
	#
	# 	if 'ingredients' and 'tags' not in validated_data:
	# 		instance.save()
	# 		return instance
	#
	# 	ingredients_data = validated_data.pop('ingredients')
	# 	tags_data = validated_data.pop('tags')
	# 	lst = []
	# 	for ingredient in ingredients_data:
	# 		current_ingredient, status = Ingredient.objects.get_or_create(
	# 			**ingredient
	# 		)
	# 		lst.append(current_ingredient)
	# 	instance.ingredients.set(lst)
	#
	# 	instance.save()
	# 	return instance


# class IngredientInRecipeSerializer(serializers.ModelSerializer):
# 	pass



class TagSerializer(serializers.ModelSerializer):
	# color = Hex2NameColor()
	class Meta:
		model = Tag
		fields = ('id', 'name', 'color', 'slug')


class SmallRecipeSerializer(serializers.ModelSerializer):
	image = Base64ImageField()

	class Meta:
		model = Recipe
		fields = ('id', 'name', 'image', 'cooking_time')
		read_only_fields = ('id', 'name', 'image', 'cooking_time')

class CustomUserCreateSerializer(UserCreateSerializer):
	class Meta:
		model = User
		fields = tuple(User.REQUIRED_FIELDS) + (
			User.USERNAME_FIELD,
			'password', 'id'
		)


class CustomUserSerializer(UserSerializer):
	is_subscribed = serializers.SerializerMethodField(read_only=True)
	class Meta:
		model = User
		fields = (
			'email',
			'id',
			'username',
			'last_name',
			'first_name',
			'is_subscribed',
		)

	def get_is_subscribed(self, obj):
		user = self.context.get('request').user
		if user.is_anonymous:
			return False
		return Follow.objects.filter(user=user, following=obj).exists()


class FollowSerializer(CustomUserSerializer):
	recipes_count = SerializerMethodField()
	recipes = SerializerMethodField()

	class Meta(CustomUserSerializer):
		fields = CustomUserSerializer.Meta.fields + (
			'recipes_count',
			'recipes',
		)
		read_only_fields = ('email', 'username')

	def validate(self, data):
		author = self.instance
		user = self.context.get('request').user
		if Follow.objects.filter(author=author, user=user).exists():
			raise ValidationError(
				message='You are already subscribed this user',
				code=status.HTTP_400_BAD_REQUEST
			)
		if user == author:
			raise ValidationError(
				message='You can not follow yourself',
				code=status.HTTP_400_BAD_REQUEST
			)
		return data

	def get_recipes_count(self, obj):
		return obj.recipes.count()

	def get_recipes(self, obj):
		request = self.context.get('request')
		limit = request.GET.get('recipes_limit')
		recipes = obj.recipes.all()
		if limit:
			recipes = recipes[:int(limit)]
		serializer = SmallRecipeSerializer(recipes, many=True, read_only=True)
		return serializer.data


