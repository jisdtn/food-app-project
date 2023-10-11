from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from djoser.views import UserViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import Follow
from .mixins import ListCreateMixin
from .pagination import CustomPagination
from .permissions import AuthorOrReadOnly
from .serializers import RecipeSerializer, FollowSerializer, TagSerializer, \
	IngredientSerializer, CustomUserSerializer
from recipes.models import Recipe, Tag, Ingredient

User = get_user_model()

# Если вы решите использовать вьюсеты, то вам потребуется добавлять дополнительные action.
# Не забывайте о том, что для разных action сериализаторы и уровни доступа (permissions) могут отличаться.
# Некоторые методы, в том числе и action, могут быть похожи друг на друга. Избегайте дублирующегося кода.
class RecipeViewSet(viewsets.ModelViewSet):
	"""List of all recipes."""

	queryset = Recipe.objects.all()
	serializer_class = RecipeSerializer
	permission_classes = (
		AuthorOrReadOnly,
		permissions.IsAuthenticatedOrReadOnly
	)
	# pagination_class = LimitOffsetPagination

	def perform_create(self, serializer):
		serializer.save(author=self.request.user)


class IngredientViewSet(viewsets.ModelViewSet):
	queryset = Ingredient.objects.all
	permission_classes = (AllowAny, )
	serializer_class = IngredientSerializer
	# filter_backends = [IngredientSearchFilter]


class FollowViewSet(ListCreateMixin):
	"""List of subscriptions."""

	serializer_class = FollowSerializer
	permission_classes = (permissions.IsAuthenticated, )
	filter_backends = (filters.SearchFilter, filters.OrderingFilter)
	search_fields = ('following__username',)
	ordering_fields = ('following',)

	def perform_create(self, serializer: FollowSerializer):
		"""Creates subcriptions. Follower is a current user."""

		serializer.save(user=self.request.user)

	def get_queryset(self):
		"""Returns the list of the subscriptions."""

		return self.request.user.follower.all()

class FavoriteViewSet(viewsets.ModelViewSet):
	pass


class TagViewSet(viewsets.ReadOnlyModelViewSet):
	"""List of the tags."""

	queryset = Tag.objects.all()
	serializer_class = TagSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
	pass


class CustomUserViewSet(UserViewSet):
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
