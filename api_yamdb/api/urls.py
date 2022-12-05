from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CommentViewSet,
    ReviewViewSet,
    TitleViewSet,
    CategoryViewSet,
    GenreViewSet,
    get_token,
    signup_new_user,
    slug_cat_destroy,
    slug_gen_destroy
)


app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('titles', TitleViewSet)
router_v1.register('categories', CategoryViewSet)
router_v1.register('genres', GenreViewSet)
router_v1.register(r'titles/(?P<title_id>[1-9]\d*)/reviews', ReviewViewSet)
router_v1.register(
    r'titles/(?P<title_id>[1-9]\d*)/reviews/(?P<review_id>[1-9]\d*)/comments',
    CommentViewSet
)

urlpatterns = [
    path('v1/auth/signup/', signup_new_user, name='auth_signup'),
    path('v1/auth/token/', get_token, name='auth_token'),
    path('v1/categories/<slug:slug>/', slug_cat_destroy),
    path('v1/genres/<slug:slug>/', slug_gen_destroy),
    path('v1/', include(router_v1.urls))
]
