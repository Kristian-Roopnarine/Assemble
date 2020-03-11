from django.urls import path
from django.contrib.auth import views as auth_views
from .views import sign_up,index

urlpatterns = [
    path('',index,name='home'),
    path('login',auth_views.LoginView.as_view(),name='login'),
    path('sign-up',sign_up,name='sign-up')
]