from django.urls import path
from django.contrib.auth import views as auth_views
from .views import sign_up,index

urlpatterns = [
    path('',index,name='home'),
    path('accounts/sign-up',sign_up,name='sign-up')
]