from django.urls import path
from . import views_templates as views

urlpatterns = [
    # Pages principales
    path('', views.acte_list, name='acte-list'),
    path('<uuid:pk>/', views.acte_detail, name='acte-detail'),
    path('nouveau/', views.acte_create, name='acte-create'),
    path('<uuid:pk>/modifier/', views.acte_update, name='acte-edit'),
    path('<uuid:pk>/valider/', views.acte_validate, name='acte-validate'),
    
    # Actions
    path('<uuid:pk>/pdf/', views.acte_download_pdf, name='acte-download-pdf'),
    
    # Suppression (pour super admin)
    path('<uuid:pk>/supprimer/', views.acte_delete, name='acte-delete'),
]
