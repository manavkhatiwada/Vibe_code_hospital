from django.urls import path
from .views import AdminUserCreateView, LoginView, ProfileView, RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('admin/users/', AdminUserCreateView.as_view()),
    path('login/', LoginView.as_view()),
    path('profile/', ProfileView.as_view()),
]