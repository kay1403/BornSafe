"""
URL configuration for bornsafe_backend project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Import des vues
from actes.views_templates import dashboard, acte_list, acte_detail, acte_create, acte_update, acte_validate, acte_download_pdf, acte_delete
from provinces.views_templates import province_list, province_create, province_update, province_delete
from accounts.views_templates import profile, change_password, user_list, user_detail, user_toggle_active, logout_view, login_view
from accounts.views_register import register_page

# Vue d'accueil
def home(request):
    from django.shortcuts import render
    return render(request, 'home.html')

schema_view = get_schema_view(
    openapi.Info(
        title="BornSafe API",
        default_version='v1',
        description="Documentation de l'API BornSafe",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@bornsafe.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# URLs API
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/provinces/', include('provinces.urls')),
    path('api/actes/', include('actes.urls')),

    # Swagger & Redoc
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# URLs Templates (interface web)
urlpatterns += [
    # Page d'accueil
    path('', home, name='home'),
    
    # Inscription
    path('inscription/', register_page, name='register-page'),
    
    # Dashboard
    path('dashboard/', dashboard, name='dashboard'),
    
    # Actes
    path('actes/', acte_list, name='acte-list'),
    path('actes/nouveau/', acte_create, name='acte-create'),
    path('actes/<uuid:pk>/', acte_detail, name='acte-detail'),
    path('actes/<uuid:pk>/modifier/', acte_update, name='acte-edit'),
    path('actes/<uuid:pk>/valider/', acte_validate, name='acte-validate'),
    path('actes/<uuid:pk>/pdf/', acte_download_pdf, name='acte-download-pdf'),
    path('actes/<uuid:pk>/supprimer/', acte_delete, name='acte-delete'),  # ✅ Maintenant acte_delete est importé
    
    # Provinces
    path('provinces/', province_list, name='province-list'),
    path('provinces/creer/', province_create, name='province-create'),
    path('provinces/<int:pk>/modifier/', province_update, name='province-edit'),
    path('provinces/<int:pk>/supprimer/', province_delete, name='province-delete'),
    
    # Comptes
    path('comptes/login/', login_view, name='login'),
    path('comptes/logout/', logout_view, name='logout'),
    path('comptes/profil/', profile, name='profile'),
    path('comptes/changer-mot-de-passe/', change_password, name='change-password'),
    path('comptes/utilisateurs/', user_list, name='user-list'),
    path('comptes/utilisateurs/<int:pk>/', user_detail, name='user-detail'),
    path('comptes/utilisateurs/<int:pk>/toggle/', user_toggle_active, name='user-toggle'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
