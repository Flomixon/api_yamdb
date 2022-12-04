from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReviewViewSet,
    CommentViewSet,
    TitleViewSet,
    get_token,
    signup_new_user
)


app_name = 'api'

router = DefaultRouter()
router.register('titles', TitleViewSet)
router.register(r'titles/(?P<title_id>[1-9]\d*)/reviews', ReviewViewSet)
router.register(
    r'titles/(?P<title_id>[1-9]\d*)/reviews/(?P<review_id>[1-9]\d*)/comments', 
    CommentViewSet
)

urlpatterns = [
    path('v1/auth/signup/', signup_new_user, name='auth_signup'),
    path('v1/auth/token/', get_token, name='auth_token'),
    path('v1/', include(router.urls)),
]
