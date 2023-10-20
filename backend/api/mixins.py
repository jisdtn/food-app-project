from rest_framework import mixins, viewsets


class ListCreateMixin(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    """Creates an object and
    returns the list of the objects."""
    pass
