from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActeNaissanceViewSet

router = DefaultRouter()
router.register(r'', ActeNaissanceViewSet, basename='acte')

urlpatterns = [
    path('', include(router.urls)),
]
