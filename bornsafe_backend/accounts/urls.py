from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserViewSet.as_view({'post': 'register'}), name='register'),
    path('login/', UserViewSet.as_view({'post': 'login'}), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserViewSet.as_view({'get': 'me'}), name='me'),
    path('update-profile/', UserViewSet.as_view({'put': 'update_profile'}), name='update-profile'),
    path('change-password/', UserViewSet.as_view({'post': 'change_password'}), name='change-password'),
]
