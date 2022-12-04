from api.mixins import CustomViewSet
from api.models import Category, Genre, Title
from api.serializers import (CategorySerializer, GenreSerializer,
                             ReadTitleSerializer, TitleSerializer)
from django.shortcuts import get_object_or_404
from rest_framework import viewsets


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'POST',):
            return TitleSerializer
        return ReadTitleSerializer


class GenreViewSet(CustomViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def perform_create(self, serializer):
        serializer.save(
            name=serializer.request.data['name'],
            slug=serializer.request.data['slug']
        )

    def perform_destroy(self, instance):
        instance = get_object_or_404(
            Genre,
            slug=self.kwargs.get('slug')
        )
        instance.delete()


class CategoryViewSet(CustomViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def perform_create(self, serializer):
        serializer.save(
            name=serializer.request.data['name'],
            slug=serializer.request.data['slug']
        )
    
    def perform_destroy(self, instance):
        instance = get_object_or_404(
            Category,
            slug=self.kwargs.get('slug')
        )
        instance.delete()
