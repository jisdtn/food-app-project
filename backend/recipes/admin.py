from django.contrib import admin
from django.contrib.admin import display
from django.contrib.auth import get_user_model

from .models import Favorite, \
    Ingredient, IngredientInRecipe, Recipe, ShoppingCart, Tag

User = get_user_model

admin.site.register(Tag)
admin.site.register(Favorite)


class IngredientInRecipeAdmin(admin.StackedInline):
    model = IngredientInRecipe
    autocomplete_fields = ("ingredient",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "author", "get_in_favorites_count")
    readonly_fields = ("get_in_favorites_count",)
    list_filter = ("author", "tags", "name")
    search_fields = ("name", "author__username")
    ordering = ("-pub_date",)
    inlines = (IngredientInRecipeAdmin,)

    @display(description="In favorite amount")
    def get_in_favorites_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["name", "measurement_unit"]
    search_fields = ("^name",)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )
