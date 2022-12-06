from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Comment, Review, Title, User, Category, Genre
from .serializers import (
    AuthSignUpSerializer,
    AuthTokenSerializer,
    CommentSerializer,
    ReviewSerializer,
    TitleSerializer,
    CategorySerializer,
    GenreSerializer,
    ReadTitleSerializer,
    UserSerializer
)
from .permission import (AdminOrReadOnly, AdminOrStaffPermission,
                          AuthorOrModerPermission, UserForSelfPermission)
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
    permission_classes = (AdminOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'POST',):
            return TitleSerializer
        return ReadTitleSerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminOrReadOnly,)


@api_view(['DELETE'])
def slug_gen_destroy(request, slug):
    if request.user.role == 'admin':
        cat = get_object_or_404(Category, slug=slug)
        cat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_403_FORBIDDEN)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrReadOnly,)

@api_view(['DELETE'])
def slug_cat_destroy(request, slug):
    if request.user.role == 'admin':
        cat = get_object_or_404(Category, slug=slug)
        cat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_403_FORBIDDEN)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        AuthorOrModerPermission]

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
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        AuthorOrModerPermission]
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


@api_view(['GET', 'PATCH'])
@permission_classes([UserForSelfPermission,])
def user_me(request):
    user = User.objects.get(username=request.user)
    if request.method == 'PATCH':
        role = user.role
        request.data['role'] = role
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post']
    permission_classes = (AdminOrStaffPermission,)


@api_view(['GET', 'PATCH', 'DELETE'])
def username_update(request, slug):
    if request.user.role == 'admin':
        user = get_object_or_404(User, username=slug)
        if request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_403_FORBIDDEN)
