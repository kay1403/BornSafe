from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from provinces.models import Province

class MairieCreationForm(UserCreationForm):
    """Formulaire pour créer un compte mairie (par super admin)"""
    
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-input'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    phone_number = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    province = forms.ModelChoiceField(
        queryset=Province.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Province rattachée"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'province', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.role = 'mairie'
        user.is_staff = True  # Les mairies ont accès à l'admin
        if commit:
            user.save()
        return user
