from django import forms
from .models import ActeNaissance
from provinces.models import Province

class ActeNaissanceForm(forms.ModelForm):
    """Formulaire pour les actes de naissance"""
    
    class Meta:
        model = ActeNaissance
        fields = [
            'numero_acte', 'nom', 'prenom', 'date_naissance',
            'lieu_naissance', 'province', 'fichier_pdf', 'status'
        ]
        widgets = {
            'numero_acte': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: ACT-2024-001'}),
            'nom': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nom de famille'}),
            'prenom': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Prénom(s)'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ville/village de naissance'}),
            'province': forms.Select(attrs={'class': 'form-select'}),
            'fichier_pdf': forms.FileInput(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'numero_acte': 'Format recommandé: ACT-ANNÉE-NUMÉRO (ex: ACT-2024-001)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre certains champs optionnels selon le contexte
        self.fields['fichier_pdf'].required = False
        self.fields['status'].required = False
        
        # Ordonner les provinces
        self.fields['province'].queryset = Province.objects.order_by('name')
    
    def clean_numero_acte(self):
        """Validation personnalisée du numéro d'acte"""
        numero = self.cleaned_data['numero_acte']
        
        # Vérifier l'unicité (sauf si c'est le même acte)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            if ActeNaissance.objects.filter(numero_acte=numero).exclude(pk=instance.pk).exists():
                raise forms.ValidationError("Ce numéro d'acte existe déjà")
        else:
            if ActeNaissance.objects.filter(numero_acte=numero).exists():
                raise forms.ValidationError("Ce numéro d'acte existe déjà")
        
        return numero
    
    def clean_date_naissance(self):
        """Validation de la date de naissance"""
        date_naissance = self.cleaned_data['date_naissance']
        from django.utils import timezone
        from datetime import date
        
        if date_naissance > date.today():
            raise forms.ValidationError("La date de naissance ne peut pas être dans le futur")
        
        return date_naissance


class ActeRechercheForm(forms.Form):
    """Formulaire de recherche d'actes"""
    numero_acte = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Numéro d\'acte'})
    )
    nom = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nom'})
    )
    prenom = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Prénom'})
    )
    province = forms.ModelChoiceField(
        queryset=Province.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'Tous')] + ActeNaissance.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
    )
