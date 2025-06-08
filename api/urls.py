from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .controllers.seed_controller import seed_database_view, seed_status_public
from .controllers.cors_test_controller import cors_test, cors_test_post
from .controllers.permission_controller import permission_all
from .views import UserCountByDepartmentView, EventViewSet

router = DefaultRouter()
router.register(r'roles', views.RoleViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'departments', views.DepartmentViewSet, basename='department')
router.register(r'events', views.EventViewSet)
router.register(r'leave-types', views.LeaveTypeViewSet)
router.register(r'leave-requests', views.LeaveRequestViewSet)

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/verify-email/', views.VerifyEmailView.as_view(),
         name='verify-email'),
    path('auth/forgot-password/', views.PasswordResetRequestView.as_view(),
         name='forgot-password'),
    path('auth/password-reset/confirm/',
         views.PasswordResetConfirmView.as_view(),
         name='password-reset-confirm'),
    path('auth/social/', views.SocialAuthView.as_view(),
         name='social-auth'),

    path('managers/', views.ManagerListView.as_view(), name='manager-list'),
    path('departments/user-count', UserCountByDepartmentView.as_view(), name='user-count-by-department'),
    path('leave-settings/', views.LeaveSettingView.as_view(), name='leave-settings'),

    # Database seeding endpoints
    path('admin/seed/', seed_database_view, name='seed-database'),
    path('seed/status/', seed_status_public, name='seed-status'),
    
    # CORS test endpoints
    path('test/cors/', cors_test, name='cors-test'),
    path('test/cors/post/', cors_test_post, name='cors-test-post'),

    # Permissions API
    path('permission-all/', permission_all, name='permission-all'),

    # API endpoints
    path('', include(router.urls)),
]