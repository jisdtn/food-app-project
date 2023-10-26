from django.urls import include, path
from rest_framework import routers

from .views import (
    FavoriteViewSet,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    TagViewSet,
)

app_name = "api"

router = routers.DefaultRouter()
router.register("recipes", RecipeViewSet, basename="recipes"),
router.register("tags", TagViewSet, basename="tags"),
router.register("ingredients", IngredientViewSet, basename="ingredients"),
router.register(
    r"recipes/(?P<recipe_id>\d+)/shopping_cart",
    ShoppingCartViewSet,
    basename="shopping_cart",
)
router.register(
    r"recipes/(?P<recipe_id>\d+)/favorite", FavoriteViewSet, basename="favorite"
)

urlpatterns = [
    path("", include(router.urls)),
]
