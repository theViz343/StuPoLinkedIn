from django.urls import include, path
from . import views
urlpatterns=[
    path('',views.index,name='index'),
    path('authorize',views.authorize,name='authorize'),
    path('auth/linkedin',views.auth_redirect,name='redirect'),
    path('register',views.register,name='register'),
    path('profile/<int:profile_id>',views.profile,name='profile'),
]