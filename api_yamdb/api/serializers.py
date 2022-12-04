from rest_framework import serializers
from .models import User, Title, Comment, Review


class AuthSignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username')


class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=50)


class TitleSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    ) 

    class Meta:
        fields = '__all__'
        read_only_fields = ('author', 'title_id')
        model = Review


class CommentSerializer(serializers.ModelSerializer): 
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    ) 

    class Meta:
        fields = '__all__'
        read_only_fields = ('author', 'review_id')
        model = Comment
