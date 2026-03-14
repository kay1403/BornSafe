from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Province

@login_required
def province_list(request):
    """Liste des provinces"""
    provinces = Province.objects.all().order_by('name')
    return render(request, 'provinces/liste.html', {'provinces': provinces})

@login_required
def province_create(request):
    """Créer une nouvelle province (super admin seulement)"""
    if request.user.role != 'super_admin':
        messages.error(request, "Action non autorisée")
        return redirect('province-list')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Province.objects.create(name=name)
            messages.success(request, f"Province {name} créée")
        return redirect('province-list')
    
    return redirect('province-list')

@login_required
def province_update(request, pk):
    """Modifier une province (super admin seulement)"""
    if request.user.role != 'super_admin':
        messages.error(request, "Action non autorisée")
        return redirect('province-list')
    
    province = get_object_or_404(Province, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            province.name = name
            province.save()
            messages.success(request, f"Province modifiée")
        return redirect('province-list')
    
    return redirect('province-list')

@login_required
def province_delete(request, pk):
    """Supprimer une province (super admin seulement)"""
    if request.user.role != 'super_admin':
        messages.error(request, "Action non autorisée")
        return redirect('province-list')
    
    province = get_object_or_404(Province, pk=pk)
    province.delete()
    messages.success(request, f"Province supprimée")
    return redirect('province-list')
