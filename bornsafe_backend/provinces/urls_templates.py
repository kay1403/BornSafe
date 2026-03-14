from django.urls import path
from . import views_templates as views

urlpatterns = [
    path('', views.province_list, name='province-list'),
    path('creer/', views.province_create, name='province-create'),
    path('<int:pk>/modifier/', views.province_update, name='province-edit'),
    path('<int:pk>/supprimer/', views.province_delete, name='province-delete'),
]
