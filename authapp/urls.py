from django.urls import path
from .views import index, loginSSO, callback, logout

urlpatterns = [
    path('', index, name='index'),
    path('auth/sso-login/', loginSSO, name='loginSSO'),
    path('auth/callback/', callback, name='callback'),
    path('auth/logout/', logout, name='logout'),
]
