import datetime

from api.models import Category, Genre, Title
from rest_framework import serializers


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name',)
        model = Genre


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name',)
        model = Category


class ReadTitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'genre', 'category',)
        model = Title


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    def validate_year(self, value):
        current_year = datetime.datetime.now().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего',
                f'Сейчас {current_year} год'
            )
        return value

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'genre', 'category',)
        model = Title
