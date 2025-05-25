from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .controllers.seed_controller import seed_database_view, seed_status_public

router = DefaultRouter()
router.register(r'roles', views.RoleViewSet)
router.register(r'users', views.UserViewSet)

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/verify-email/', views.VerifyEmailView.as_view(),
         name='verify-email'),
    path('auth/password-reset/', views.PasswordResetRequestView.as_view(),
         name='password-reset'),
    path('auth/password-reset/confirm/',
         views.PasswordResetConfirmView.as_view(),
         name='password-reset-confirm'),
    path('auth/social/', views.SocialAuthView.as_view(),
         name='social-auth'),

    # Database seeding endpoints
    path('admin/seed/', seed_database_view, name='seed-database'),
    path('seed/status/', seed_status_public, name='seed-status'),

    # API endpoints
    path('', include(router.urls)),
]