from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import LimitOffsetPagination
from djoser.views import UserViewSet
from rest_framework.permissions import AllowAny

from .mixins import ListCreateMixin
from .permissions import AuthorOrReadOnly
from .serializers import RecipeSerializer, FollowSerializer, TagSerializer, \
	IngredientSerializer
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

# class UserListViewSet(viewsets.ReadOnlyModelViewSet):
# 	"""List of the users."""
#
# 	queryset = User.objects.all()
# 	serializer_class = UserListSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
	pass


# class CustomUserViewSet(UserViewSet):
# 	serializer_class = CustomUserSerializer