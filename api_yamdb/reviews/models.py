from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Category(models.Model):
    """Модель категорий."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)


class Genre(models.Model):
    """Модель жанров."""

    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)


class Title(models.Model):
    """Модель произведений."""

    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField(null=True)
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='genres'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произвдения'
        ordering = ('name',)


class GenreTitle(models.Model):
    """Модель произведний и жанров."""

    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='genre'
    )
    titlegit = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='title'
    )

    def __str__(self) -> str:
        return f'Жанр {self.title}: {self.genre}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['genre', 'titlegit'],
                name='unique_genr_title'
            )
        ]
        verbose_name = 'Жанр и произведение'
        verbose_name_plural = 'Жанры и произведения'


class CustomUser(AbstractUser):

    ROLE_USER = 'user'
    ROLE_MODERATOR = 'moderator'
    ROLE_ADMIN = 'admin'

    USER_ROLE_CHOICES = (
        (ROLE_USER, 'Пользователь'),
        (ROLE_MODERATOR, 'Модератор'),
        (ROLE_ADMIN, 'Администратор'),
    )

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Электронная почта'
    )
    role = models.CharField(
        max_length=16,
        choices=USER_ROLE_CHOICES,
        default=ROLE_USER,
        verbose_name='Роль'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Фамилия'
    )
    confirmation_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Код для авторизации'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email'
            )
        ]

    @property
    def is_user(self):
        if self.role == self.ROLE_USER:
            return True
        else:
            return False

    @property
    def is_moderator(self):
        if self.role == self.ROLE_MODERATOR:
            return True
        else:
            return False

    @property
    def is_admin(self):
        if self.role == self.ROLE_ADMIN:
            return True
        else:
            return False


User = get_user_model()


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='score')
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    score = models.IntegerField(
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]


class Comment(models.Model):
    review_id = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
