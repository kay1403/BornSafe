from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import Province
from django.contrib.auth import get_user_model

User = get_user_model()

class ProvinceModelTests(TestCase):
    """Tests pour le modèle Province"""
    
    def setUp(self):
        self.province = Province.objects.create(name='Kinshasa')
    
    def test_province_creation(self):
        """Test création province"""
        self.assertEqual(self.province.name, 'Kinshasa')
        self.assertEqual(str(self.province), 'Kinshasa')
    
    def test_province_unique_name(self):
        """Test unicité du nom"""
        with self.assertRaises(Exception):
            Province.objects.create(name='Kinshasa')


class ProvinceAPITests(APITestCase):
    """Tests API pour Provinces"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Créer utilisateurs
        self.user = User.objects.create_user(
            username='normaluser',
            password='UserPass123!',
            role='user'
        )
        
        self.super_admin = User.objects.create_user(
            username='superadmin',
            password='SuperPass123!',
            role='super_admin',
            is_staff=True,
            is_superuser=True
        )
        
        # Créer provinces
        self.province1 = Province.objects.create(name='Kinshasa')
        self.province2 = Province.objects.create(name='Lubumbashi')
        
        self.provinces_url = reverse('province-list')
    
    def test_1_list_provinces_authenticated(self):
        """Test 1: Lister provinces (authentifié)"""
        # Login user normal
        login_data = {'nom_utilisateur': 'normaluser', 'mot_de_passe': 'UserPass123!'}
        response = self.client.post(reverse('login'), login_data, format='json')
        token = response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Lister provinces
        response = self.client.get(self.provinces_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_2_list_provinces_unauthenticated(self):
        """Test 2: Lister provinces (non authentifié)"""
        response = self.client.get(self.provinces_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_3_create_province_super_admin(self):
        """Test 3: Créer province (super admin)"""
        # Login super admin
        login_data = {'nom_utilisateur': 'superadmin', 'mot_de_passe': 'SuperPass123!'}
        response = self.client.post(reverse('login'), login_data, format='json')
        token = response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Créer province
        data = {'nom': 'Goma'}
        response = self.client.post(self.provinces_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Province.objects.count(), 3)
    
    def test_4_create_province_normal_user(self):
        """Test 4: Créer province (user normal)"""
        # Login user normal
        login_data = {'nom_utilisateur': 'normaluser', 'mot_de_passe': 'UserPass123!'}
        response = self.client.post(reverse('login'), login_data, format='json')
        token = response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Tenter création
        data = {'nom': 'Goma'}
        response = self.client.post(self.provinces_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_5_update_province_super_admin(self):
        """Test 5: Modifier province (super admin)"""
        # Login super admin
        login_data = {'nom_utilisateur': 'superadmin', 'mot_de_passe': 'SuperPass123!'}
        response = self.client.post(reverse('login'), login_data, format='json')
        token = response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Modifier
        url = reverse('province-detail', args=[self.province1.id])
        data = {'nom': 'Kinshasa Ville'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.province1.refresh_from_db()
        self.assertEqual(self.province1.name, 'Kinshasa Ville')
    
    def test_6_delete_province_super_admin(self):
        """Test 6: Supprimer province (super admin)"""
        # Login super admin
        login_data = {'nom_utilisateur': 'superadmin', 'mot_de_passe': 'SuperPass123!'}
        response = self.client.post(reverse('login'), login_data, format='json')
        token = response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Supprimer
        url = reverse('province-detail', args=[self.province1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Province.objects.count(), 1)
