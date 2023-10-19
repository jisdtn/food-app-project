from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from djoser.views import UserViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from users.models import Follow
from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import AuthorOrAdminOrReadOnly
from .serializers import RecipeSerializer, FollowSerializer, TagSerializer, \
	IngredientSerializer, CustomUserSerializer, RecipeListSerializer, FavoriteSerializer, ShoppingCartSerializer
from recipes.models import Recipe, Tag, Ingredient, Favorite, ShoppingCart, IngredientInRecipe

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
	"""CRUD for recipes."""

	queryset = Recipe.objects.all()
	permission_classes = [AuthorOrAdminOrReadOnly, ]
	pagination_class = CustomPagination
	filterset_class = RecipeFilter
	filter_backends = [DjangoFilterBackend, ]

	def perform_create(self, serializer):
		serializer.save(author=self.request.user)

	def get_serializer_class(self):
		if self.request.method == 'GET':
			return RecipeListSerializer
		return RecipeSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
	"""List of the ingredients."""
	queryset = Ingredient.objects.all()
	permission_classes = (AllowAny, )
	serializer_class = IngredientSerializer
	filter_backends = (DjangoFilterBackend,)
	filterset_class = IngredientSearchFilter


class FavoriteViewSet(viewsets.ModelViewSet):
	"""List of the favorited recipes."""
	queryset = Favorite.objects.all()
	serializer_class = FavoriteSerializer
	pagination_class = CustomPagination
	permission_classes = [IsAuthenticated, ]

	@action(
		detail=True,
		methods=['post'])
	def add_to_fav(self, request, pk):
		recipe = get_object_or_404(Recipe, id=pk)
		value = {
			'user': request.user.id,
			'recipe': id
		}
		if not Favorite.objects.filter(user=request.user, recipe=recipe).exists():
			serializer = FavoriteSerializer(value=value, context={'request': request})
			if serializer.is_valid():
				serializer.save()
				return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(status=status.HTTP_400_BAD_REQUEST)

	@action(
		detail=True,
		methods=['delete'])
	def delete_from_fav(self, request, pk):
		recipe = get_object_or_404(Recipe, id=pk)
		if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
			Favorite.objects.filter(user=request.user, recipe=recipe).delete()
			return Response(status=status.HTTP_204_NO_CONTENT)
		return Response(status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
	"""Tags representation."""

	queryset = Tag.objects.all()
	serializer_class = TagSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
	"""Shopping Cart actions"""
	permission_classes = [IsAuthenticated, ]
	queryset = ShoppingCart.objects.all()
	serializer_class = ShoppingCartSerializer
	pagination_class = CustomPagination
	@action(
		detail=True,
		methods=['post'])
	def add_to_shopping_cart(self, request, pk):
		recipe = get_object_or_404(Recipe, id=pk)
		value = {
			'user': request.user.id,
			'recipe': id
		}
		if not ShoppingCart.objects.filter(user=request.user, recipe=recipe).exists():
			serializer = ShoppingCartSerializer(value=value, context={'request': request})
			if serializer.is_valid():
				serializer.save()
				return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(status=status.HTTP_400_BAD_REQUEST)

	@action(
		detail=True,
		methods=['delete'])
	def delete_from_shopping_cart(self, request, pk):
		recipe = get_object_or_404(Recipe, id=pk)
		if ShoppingCart.objects.filter(user=request.user, recipe=recipe).exists():
			ShoppingCart.objects.filter(user=request.user, recipe=recipe).delete()
			return Response(status=status.HTTP_204_NO_CONTENT)
		return Response(status=status.HTTP_400_BAD_REQUEST)

	@action(
		detail=False,
		permission_classes=[IsAuthenticated],
		methods=['get'])
	def download_shopping_cart(self, request):
		user = request.user
		if not user.shopping_cart.exists():
			return Response(status=status.HTTP_400_BAD_REQUEST)

		ingredients = IngredientInRecipe.objects.filter(recipe__shopping_cart__user=request.user).values(
			'ingredient__name',
			'ingredient__measurement_unit'
		).annotate(amount=Sum('amount'))

		shopping_list = 'Groceries list'
		for ingredient in ingredients:
			shopping_list += (
				f"\n{ingredient['ingredient__name']} "
				f"{ingredient['ingredient__amount']} {ingredient['ingredient__measurement_unit']}"
			)
		file = f'{user.username}_shopping_list.pdf'
		response = HttpResponse(shopping_list, content_type='application/pdf')
		response['Content-Disposition'] = f'attachment; filename={file}'
		return response


class CustomUserViewSet(UserViewSet):
	"""Users actions."""
	queryset = User.objects.all()
	serializer_class = CustomUserSerializer
	pagination_class = CustomPagination

	@action(
		detail=True,
		methods=['post', 'delete'],
		permission_classes=[IsAuthenticated]
	)
	def subscribe(self, request, **kwargs):
		user = request.user
		author_id = self.kwargs.get('id')
		author = get_object_or_404(User, id=author_id)

		if request.method == 'POST':
			serializer = FollowSerializer(author,
			                              data=request.data,
			                              context={'request': request})
			serializer.is_valid(raise_exception=True)
			Follow.objects.create(user=user, author=author)
			return Response(serializer.data, status=status.HTTP_201_CREATED)

		if request.method == 'DELETE':
			subscription = get_object_or_404(Follow,
			                                 user=user,
			                                 author=author)
			subscription.delete()
			return Response(status=status.HTTP_204_NO_CONTENT)

	@action(
		detail=False,
		permission_classes=[IsAuthenticated]
	)
	def subscriptions(self, request):
		user = request.user
		queryset = User.objects.filter(following__user=user)
		pages = self.paginate_queryset(queryset)
		serializer = FollowSerializer(pages,
		                              many=True,
		                              context={'request': request})
		return self.get_paginated_response(serializer.data)
