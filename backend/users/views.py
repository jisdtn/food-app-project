from api.pagination import CustomPagination
from api.serializers import FollowSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Follow

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Users actions."""

    queryset = User.objects.all()
    pagination_class = CustomPagination
    link_model = Follow

    def get_permissions(self):
        if self.action == "me":
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(detail=True, methods=("post",), permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        user = request.user
        following_id = self.kwargs.get("id")
        following = get_object_or_404(User, id=following_id)

        serializer = FollowSerializer(
            following, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        Follow.objects.create(user=user, following=following)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, **kwargs):
        user = request.user
        following_id = self.kwargs.get("id")
        following = get_object_or_404(User, id=following_id)
        subscription = Follow.objects.filter(user=user, following=following)
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "You can not unsubscribe twice"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(pages, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)
