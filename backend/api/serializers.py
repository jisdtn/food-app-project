from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import F
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from rest_framework import serializers, status
from rest_framework.fields import SerializerMethodField
from users.models import Follow

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = (
            "id",
            "amount",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "last_name",
            "first_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if not request:
            return False
        user = request.user
        return (
            user
            and user.is_authenticated
            and user.following.filter(following=obj).exists()
        )


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = AddIngredientSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )

    def validate(self, data):
        if "ingredients" not in data:
            raise serializers.ValidationError(
                "you need at least one ingredient"
            )

        if "tags" not in data:
            raise serializers.ValidationError(
                "you have to choose at least one tag"
            )

        if not data["image"]:
            raise serializers.ValidationError("add a picture")

        return data

    def validate_ingredients(self, ingredients):
        if len(ingredients) == 0:
            raise ValidationError("you need at least one ingredient")
        ingredients_list = []
        for i in ingredients:
            try:
                ingredient = get_object_or_404(Ingredient, id=i["id"])
            except Exception:
                raise serializers.ValidationError(
                    "ingredient does not exist"
                )

            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    "ingredients should be unique"
                )
            if int(i["amount"]) <= 0:
                raise serializers.ValidationError(
                    "ingredient amount should be at least 1"
                )
            ingredients_list.append(ingredient)

        return ingredients

    def validate_tags(self, tags):
        if len(tags) == 0:
            raise serializers.ValidationError(
                "you have to choose at least one tag"
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError("tags should be unique")

        return tags

    def create_ingredients(self, ingredients, recipe):
        if not ingredients:
            raise serializers.ValidationError(
                "you need at least one ingredient"
            )
        for i in ingredients:
            ingredient = Ingredient.objects.get(id=i["id"])
            IngredientInRecipe.objects.create(
                ingredient=ingredient, recipe=recipe, amount=i["amount"]
            )

    def create(self, validated_data):
        image = validated_data.pop("image")
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get("image", instance.image)
        tags_data = validated_data.pop("tags", OrderedDict())
        ingredients = validated_data.pop("ingredients", OrderedDict())
        instance = super().update(instance, validated_data)
        instance.tags.set(tags_data)
        instance.ingredients.clear()
        self.create_ingredients(recipe=instance, ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return RecipeListSerializer(instance, context=context).data


class RecipeListSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = RecipeSerializer.Meta.fields + (
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            "id",
            "name",
            "measurement_unit",
            amount=F("ingredientinrecipe__amount")
        )
        return ingredients

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request:
            return False
        user = request.user
        return (
            user
            and user.is_authenticated
            and user.favorite.filter(recipe_id=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if not request:
            return False
        user = request.user
        return (
            user
            and user.is_authenticated
            and user.shopping_cart.filter(recipe_id=obj).exists()
        )


class SmallRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + ("email", "password", "id")


class FollowSerializer(CustomUserSerializer):
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        model = User
        fields = CustomUserSerializer.Meta.fields + (
            "recipes_count",
            "recipes",
        )
        read_only_fields = ("email", "username")

    def validate(self, data):
        following = self.instance
        request = self.context.get("request")
        if not request:
            return False
        user = request.user
        if Follow.objects.filter(following=following, user=user).exists():
            raise serializers.ValidationError(
                "You are already subscribed to this user",
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == following:
            raise serializers.ValidationError(
                "You can not follow yourself", code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get("request")
        if not request:
            return False
        limit = request.GET.get("recipes_limit")
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = SmallRecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data
