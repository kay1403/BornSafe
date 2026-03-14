from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, logout, authenticate, login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse

User = get_user_model()

def login_view(request):
    """Connexion personnalisée avec session explicite"""
    # Si déjà connecté, rediriger vers dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authentifier l'utilisateur
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Connexion explicite avec création de session
            login(request, user)
            
            # Forcer la sauvegarde de la session
            request.session.save()
            
            # Vérifier que la session est bien créée
            if not request.session.session_key:
                request.session.create()
            
            messages.success(request, f"Bienvenue {user.username} !")
            
            # Redirection explicite vers dashboard
            return HttpResponseRedirect(reverse('dashboard'))
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
    
    return render(request, 'accounts/login.html')

@login_required
def profile(request):
    """Voir et modifier son profil"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.save()
        messages.success(request, "Profil mis à jour avec succès")
        return redirect('profile')
    
    return render(request, 'accounts/profil.html')

@login_required
def change_password(request):
    """Changer le mot de passe"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Mot de passe changé avec succès")
            return redirect('profile')
        else:
            messages.error(request, "Erreur lors du changement de mot de passe")
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def user_list(request):
    """Liste des utilisateurs (admin seulement)"""
    if request.user.role != 'super_admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dashboard')
    
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
def user_detail(request, pk):
    """Détail d'un utilisateur (admin seulement)"""
    if request.user.role != 'super_admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=pk)
    return render(request, 'accounts/user_detail.html', {'user': user})

@login_required
def user_toggle_active(request, pk):
    """Activer/désactiver un utilisateur"""
    if request.user.role != 'super_admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save()
    
    status = "activé" if user.is_active else "désactivé"
    messages.success(request, f"Compte {user.username} {status}")
    return redirect('user-list')

def logout_view(request):
    """Déconnexion"""
    logout(request)
    return redirect('home')
