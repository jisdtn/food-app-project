from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    measurement_unit = models.CharField(max_length=50)

    class Meta:
        unique_together = ("name", "measurement_unit")
        ordering = ("name",)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=16)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    ingredients = models.ManyToManyField(Ingredient, through="IngredientInRecipe")
    tags = models.ManyToManyField(Tag, related_name="recipes")
    image = models.ImageField(upload_to="recipes/images", null=True, blank=True)
    name = models.CharField(max_length=200)
    text = models.TextField()
    cooking_time = models.IntegerField(validators=[MinValueValidator(1)])
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        ordering = ("-pub_date",)
        constraints = [
            models.UniqueConstraint(fields=["name", "author"], name="recipe_unique")
        ]

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredientinrecipe"
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )

    def __str__(self):
        return f'Ingredient "{self.ingredient}" for the "{self.recipe}" recipe'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorite", verbose_name="User"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite",
        verbose_name="Recipe",
    )
    date_added = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
        verbose_name="Added",
    )

    class Meta:
        verbose_name = "Favorite"
        verbose_name_plural = "Favorite"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="favorite_user_recept_unique"
            )
        ]

    def __str__(self):
        return f'Рецепт "{self.recipe}" в избранном у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="User",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Recipe",
    )

    class Meta:
        verbose_name = "Shopping_cart"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="shopping_cart_user_recept_unique"
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Список покупок'
