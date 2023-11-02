from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import AuthorOrAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeListSerializer,
                          RecipeSerializer, SmallRecipeSerializer,
                          TagSerializer)

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    """CRUD for recipes."""

    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrAdminOrReadOnly,)
    pagination_class = CustomPagination
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeListSerializer
        return RecipeSerializer

    @action(
        detail=True, methods=["POST", "DELETE"], permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        if request.method == "POST":
            return self.add_obj(Favorite, request.user, pk)
        else:
            return self.delete_obj(Favorite, request.user, pk)

    @action(
        detail=True, methods=["POST", "DELETE"], permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        if request.method == "POST":
            return self.add_obj(ShoppingCart, request.user, pk)
        else:
            return self.delete_obj(ShoppingCart, request.user, pk)

    def add_obj(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {"error": "The recipe is already added"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            recipe = get_object_or_404(Recipe, id=pk)
        except Exception:
            raise serializers.ValidationError("The recipe does not exist")
        model.objects.create(user=user, recipe=recipe)
        serializer = SmallRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_obj(self, model, user, pk):
        try:
            get_object_or_404(Recipe, id=pk)
        except Exception:
            raise Http404
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "The recipe is already deleted"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = (
            IngredientInRecipe.objects.filter(recipe__shopping_cart__user=request.user)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
        )

        shopping_list = "Groceries list"
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredient__name']} "
                f"{ingredient['amount']} "
                f"{ingredient['ingredient__measurement_unit']}"
            )
        file = f"{user.username}_shopping_list.pdf"
        response = HttpResponse(shopping_list, "Content-Type: application/pdf")
        response["Content-Disposition"] = f"attachment; filename={file}"
        return response


class IngredientViewSet(ReadOnlyModelViewSet):
    """List of the ingredients."""

    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter


class TagViewSet(ReadOnlyModelViewSet):
    """Tags representation."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
