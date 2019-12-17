from django.urls import path

from apps.user_profile import views

app_name = 'user_profile'

urlpatterns = [
    # path('logout/', views.UserLogoutView.as_view(), name='user_logout'),
    # path('login/', views.UserLoginView.as_view(), name='login'),
    path('register/', views.UserRegisterView.as_view(), name='register')
]