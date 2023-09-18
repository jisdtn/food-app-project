from django.urls import include, path
from rest_framework import routers

from .views import RecipeViewSet, TagViewSet, IngredientViewSet, UserViewSet, ShoppingCartViewSet, FavoriteViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes'),
router.register('tags', TagViewSet, basename='tags'),
router.register('ingredients', IngredientViewSet, basename='ingredients'),
router.register('users', UserViewSet, basename='users'),
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shopping_cart'
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorite'
)


urlpatterns = [
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
    path('v1/', include(router.urls)),
]