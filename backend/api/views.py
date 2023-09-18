from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import LimitOffsetPagination

from .mixins import ListCreateMixin
from .permissions import AuthorOrReadOnly
from .serializers import RecipeSerializer, FollowSerializer, TagSerializer, UserSerializer
from recipes.models import Recipe, Tag
from users.models import User


class RecipeViewSet(viewsets.ModelViewSet):
	"""List of all recipes."""

	queryset = Recipe.objects.all()
	serializer_class = RecipeSerializer
	permission_classes = (
		AuthorOrReadOnly,
		permissions.IsAuthenticatedOrReadOnly
	)
	pagination_class = LimitOffsetPagination

	def perform_create(self, serializer):
		serializer.save(author=self.request.user)


class IngredientViewSet(viewsets.ModelViewSet):
	pass


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

class UserViewSet(viewsets.ReadOnlyModelViewSet):
	"""List of the users."""

	queryset = User.objects.all()
	serializer_class = UserSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
	pass

