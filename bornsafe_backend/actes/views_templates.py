from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from .models import ActeNaissance
from provinces.models import Province
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def dashboard(request):
    """Tableau de bord principal"""
    
    # Statistiques générales
    total_actes = ActeNaissance.objects.count()
    actes_valides = ActeNaissance.objects.filter(status='valide').count()
    actes_attente = ActeNaissance.objects.filter(status='brouillon').count()
    total_users = User.objects.count()
    users_actifs = User.objects.filter(is_active=True).count()
    
    # Actes récents
    actes_recents = ActeNaissance.objects.select_related('province').order_by('-created_at')[:5]
    
    # Statistiques par province
    stats_provinces = Province.objects.annotate(
        total=Count('actes_naissance'),
        valides=Count('actes_naissance', filter=Q(actes_naissance__status='valide')),
        brouillons=Count('actes_naissance', filter=Q(actes_naissance__status='brouillon')),
        annules=Count('actes_naissance', filter=Q(actes_naissance__status='annule'))
    )
    
    context = {
        'total_actes': total_actes,
        'actes_valides': actes_valides,
        'actes_attente': actes_attente,
        'total_users': total_users,
        'users_actifs': users_actifs,
        'actes_recents': actes_recents,
        'stats_provinces': stats_provinces,
        'taux_validation': int((actes_valides / total_actes * 100)) if total_actes > 0 else 0,
        'current_date': timezone.now(),
    }
    return render(request, 'dashboard.html', context)

@login_required
def acte_list(request):
    """Liste des actes"""
    queryset = ActeNaissance.objects.select_related('province', 'created_by').all()
    
    # Filtrage par rôle
    if request.user.role == 'mairie':
        queryset = queryset.filter(created_by=request.user)
    elif request.user.role == 'user':
        queryset = queryset.filter(status='valide')
    
    # Recherche
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(numero_acte__icontains=search_query) |
            Q(nom__icontains=search_query) |
            Q(prenom__icontains=search_query)
        )
    
    # Filtre province
    province_id = request.GET.get('province')
    if province_id:
        queryset = queryset.filter(province_id=province_id)
    
    # Filtre statut
    status = request.GET.get('status')
    if status:
        queryset = queryset.filter(status=status)
    
    # Pagination
    paginator = Paginator(queryset.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    actes = paginator.get_page(page_number)
    
    context = {
        'actes': actes,
        'provinces': Province.objects.all(),
        'is_paginated': actes.has_other_pages(),
        'page_obj': actes,
        'paginator': paginator,
    }
    return render(request, 'actes/liste.html', context)

@login_required
def acte_detail(request, pk):
    """Détail d'un acte"""
    acte = get_object_or_404(ActeNaissance, pk=pk)
    
    # Vérification des permissions
    if request.user.role == 'user' and acte.status != 'valide':
        messages.error(request, "Vous n'avez pas accès à cet acte")
        return redirect('acte-list')
    
    if request.user.role == 'mairie' and acte.created_by != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à voir cet acte")
        return redirect('acte-list')
    
    context = {'acte': acte}
    return render(request, 'actes/detail.html', context)

@login_required
def acte_create(request):
    """Création d'un acte"""
    if request.user.role not in ['mairie', 'super_admin']:
        messages.error(request, "Vous n'êtes pas autorisé à créer des actes")
        return redirect('acte-list')
    
    from .forms import ActeNaissanceForm
    
    if request.method == 'POST':
        form = ActeNaissanceForm(request.POST, request.FILES)
        if form.is_valid():
            acte = form.save(commit=False)
            acte.created_by = request.user
            acte.modified_by = request.user
            acte.save()
            messages.success(request, f"Acte {acte.numero_acte} créé avec succès")
            return redirect('acte-detail', pk=acte.id)
    else:
        form = ActeNaissanceForm()
    
    context = {'form': form, 'acte': None}
    return render(request, 'actes/formulaire.html', context)

@login_required
def acte_update(request, pk):
    """Modification d'un acte"""
    acte = get_object_or_404(ActeNaissance, pk=pk)
    
    if request.user.role not in ['mairie', 'super_admin']:
        messages.error(request, "Vous n'êtes pas autorisé à modifier des actes")
        return redirect('acte-list')
    
    if request.user.role == 'mairie' and acte.created_by != request.user:
        messages.error(request, "Vous ne pouvez modifier que vos propres actes")
        return redirect('acte-list')
    
    from .forms import ActeNaissanceForm
    
    if request.method == 'POST':
        form = ActeNaissanceForm(request.POST, request.FILES, instance=acte)
        if form.is_valid():
            acte = form.save(commit=False)
            acte.modified_by = request.user
            acte.save()
            messages.success(request, f"Acte {acte.numero_acte} modifié avec succès")
            return redirect('acte-detail', pk=acte.id)
    else:
        form = ActeNaissanceForm(instance=acte)
    
    context = {'form': form, 'acte': acte}
    return render(request, 'actes/formulaire.html', context)

@login_required
def acte_validate(request, pk):
    """Validation d'un acte"""
    if request.method == 'POST':
        acte = get_object_or_404(ActeNaissance, pk=pk)
        
        if request.user.role not in ['mairie', 'super_admin']:
            messages.error(request, "Vous n'êtes pas autorisé à valider des actes")
            return redirect('acte-list')
        
        if acte.status != 'brouillon':
            messages.error(request, "Cet acte ne peut pas être validé")
            return redirect('acte-detail', pk=acte.id)
        
        acte.status = 'valide'
        acte.modified_by = request.user
        acte.save()
        
        messages.success(request, f"Acte {acte.numero_acte} validé avec succès")
    
    return redirect('acte-detail', pk=pk)

@login_required
def acte_download_pdf(request, pk):
    """Télécharger le PDF d'un acte"""
    acte = get_object_or_404(ActeNaissance, pk=pk)
    
    if not acte.fichier_pdf:
        messages.error(request, "PDF non disponible")
        return redirect('acte-detail', pk=acte.id)
    
    from django.http import FileResponse
    return FileResponse(
        acte.fichier_pdf, 
        as_attachment=True,
        filename=f"acte_{acte.numero_acte}.pdf"
    )
