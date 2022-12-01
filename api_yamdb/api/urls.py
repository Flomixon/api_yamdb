
from django.urls import path
from .views import (get_token,
                    signup_new_user)

app_name = 'api'

urlpatterns = [
    path('v1/auth/signup/', signup_new_user, name='auth_signup'),
    path('v1/auth/token/', get_token, name='auth_token')
]