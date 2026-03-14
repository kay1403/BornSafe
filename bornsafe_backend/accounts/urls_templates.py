from django.urls import path
from django.contrib.auth import views as auth_views
from . import views_templates as views

urlpatterns = [
    # Authentification
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Profil
    path('profil/', views.profile, name='profile'),
    path('changer-mot-de-passe/', views.change_password, name='change-password'),
    
    # Gestion des utilisateurs (admin seulement)
    path('utilisateurs/', views.user_list, name='user-list'),
    path('utilisateurs/<int:pk>/', views.user_detail, name='user-detail'),
    path('utilisateurs/<int:pk>/toggle/', views.user_toggle_active, name='user-toggle'),
    
    # Création de mairie (super admin seulement)
    path('mairie/creer/', views.mairie_create, name='mairie-create'),
]
