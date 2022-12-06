from api.filters import TitleFilter
from api.mixins import CustomViewSet
from api.models import Category, Genre, Title
from api.serializers import (CategorySerializer, GenreSerializer,
                             ReadTitleSerializer, TitleSerializer)
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Comment, Review, Title, User
from .serializers import (AuthSignUpSerializer, AuthTokenSerializer,
                          CommentSerializer, ReviewSerializer, TitleSerializer)
from .utils import send_confirmation_code_to_email


@api_view(['POST'])
def signup_new_user(request):
    """Регистрируем нового пользователя"""
    username = request.data.get('username')
    if not User.objects.filter(username=username).exists():
        serializer = AuthSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['username'] != 'me':
            serializer.save()
            send_confirmation_code_to_email(username)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            'Имя указан невено!', status=status.HTTP_400_BAD_REQUEST
        )
    user = get_object_or_404(User, username=username)
    serializer = AuthSignUpSerializer(
        user, data=request.data, partial=True
    )
    serializer.is_valid(raise_exception=True)
    if serializer.validated_data['email'] == user.email:
        serializer.save()
        send_confirmation_code_to_email(username)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(
        'Почта указана неверно!', status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
def get_token(request):
    """Получаем JWT токен"""
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            'Пользователь отсутсвует', status=status.HTTP_404_NOT_FOUND
        )
    if user.confirmation_code == confirmation_code:
        refresh = RefreshToken.for_user(user)
        token_data = {'token': str(refresh.access_token)}
        return Response(token_data, status=status.HTTP_200_OK)
    return Response(
        'Неверный код подтверждения', status=status.HTTP_400_BAD_REQUEST
    )


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'POST',):
            return TitleSerializer
        return ReadTitleSerializer


class GenreViewSet(CustomViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

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
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

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


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    """ permission_classes = (
        IsAuthorOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly
    ) """

    def list(self, request, title_id):
        title = Title.objects.get(id=title_id)
        queryset = title.reviews.all()
        serializer = ReviewSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        queryset = Review.objects.filter(
            author=self.request.user,
            title_id=self.kwargs['title_id']
        )
        if queryset.exists():
            raise ValidationError('Нельзя добавлять более одного отзыва!')
        serializer.save(
            author=self.request.user,
            title_id=Title.objects.get(id=self.kwargs['title_id'])
        )


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    """ permission_classes = (
        IsAuthorOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly
    ) """

    def list(self, request, title_id, review_id):
        review = Review.objects.get(id=review_id)
        queryset = review.comments.all()
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review_id=Review.objects.get(id=self.kwargs['review_id'])
        )
