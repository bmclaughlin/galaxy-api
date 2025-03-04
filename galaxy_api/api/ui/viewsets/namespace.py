from django_filters import filters
from django_filters.rest_framework import filterset, DjangoFilterBackend

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.settings import api_settings

from galaxy_api.api import models, permissions
from galaxy_api.api.ui import serializers


class NamespaceFilter(filterset.FilterSet):
    keywords = filters.CharFilter(method='keywords_filter')

    sort = filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('company', 'company'),
            ('id', 'id'),
        ),
    )

    class Meta:
        model = models.Namespace
        fields = ('name', 'company',)

    def keywords_filter(self, queryset, name, value):

        keywords = self.request.query_params.getlist('keywords')

        for keyword in keywords:
            queryset = queryset.filter(name=keyword)

        return queryset


class NamespaceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "name"
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [
        permissions.IsNamespaceOwnerOrReadOnly
    ]

    filter_backends = (DjangoFilterBackend,)

    filterset_class = NamespaceFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.NamespaceSummarySerializer
        else:
            return serializers.NamespaceSerializer

    def get_queryset(self):
        return models.Namespace.objects.all()


class MyNamespaceViewSet(NamespaceViewSet):
    def get_queryset(self):
        # FIXME(cutwater): this view should aso return all the namespaces if
        # the user is part of the partner engineering team. Don't know how
        # we plan to handle that.
        return models.Namespace.objects.filter(
            groups__in=self.request.user.groups.all())
