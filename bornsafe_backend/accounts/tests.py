from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import json
import tempfile
from PIL import Image

User = get_user_model()

class UserModelTests(TestCase):
    """Tests approfondis pour le modèle User"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User',
            phone_number='+243123456789'
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='AdminPass123!',
            first_name='Admin',
            last_name='User',
            role='super_admin',
            is_staff=True
        )
    
    def test_user_creation(self):
        """Test la création d'utilisateur"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@test.com')
        self.assertTrue(self.user.check_password('TestPass123!'))
        self.assertEqual(self.user.role, 'user')
        self.assertEqual(self.user.phone_number, '+243123456789')
        self.assertFalse(self.user.is_staff)
    
    def test_admin_creation(self):
        """Test la création d'admin"""
        self.assertEqual(self.admin.role, 'super_admin')
        self.assertTrue(self.admin.is_staff)
    
    def test_user_str_method(self):
        """Test la méthode __str__"""
        self.assertEqual(str(self.user), "testuser (Utilisateur)")
    
    def test_failed_login_tracking(self):
        """Test le suivi des tentatives échouées"""
        # Test initial
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.assertFalse(self.user.is_account_locked())
        
        # 3 tentatives échouées
        for i in range(3):
            self.user.record_failed_login()
        self.assertEqual(self.user.failed_login_attempts, 3)
        self.assertFalse(self.user.is_account_locked())
        
        # 5 tentatives échouées (verrouillage)
        for i in range(2):
            self.user.record_failed_login()
        self.assertEqual(self.user.failed_login_attempts, 5)
        self.assertTrue(self.user.is_account_locked())
        
        # Test réinitialisation
        self.user.reset_failed_login_attempts()
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.assertFalse(self.user.is_account_locked())
    
    def test_unique_constraints(self):
        """Test les contraintes d'unicité"""
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='testuser',  # Déjà existant
                email='autre@test.com',
                password='password123'
            )
        
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='autreuser',
                email='test@test.com',  # Déjà existant
                password='password123'
            )


class UserAPITests(APITestCase):
    """Tests API pour User"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.me_url = reverse('me')
        self.change_password_url = reverse('change-password')
        
        # Données valides
        self.valid_user_data = {
            'nom_utilisateur': 'nouvelutilisateur',
            'email': 'nouveau@test.com',
            'mot_de_passe': 'TestPass123!',
            'confirmation_mot_de_passe': 'TestPass123!',
            'nom': 'Nouveau',
            'prenom': 'Utilisateur',
            'telephone': '+243123456789'
        }
    
    def test_1_registration_success(self):
        """Test 1: Enregistrement réussi"""
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], self.valid_user_data['email'])
        
        # Vérifier que l'utilisateur est bien créé
        user = User.objects.get(username='nouvelutilisateur')
        self.assertEqual(user.first_name, 'Nouveau')
        self.assertEqual(user.role, 'user')
    
    def test_2_registration_password_mismatch(self):
        """Test 2: Mots de passe différents"""
        data = self.valid_user_data.copy()
        data['confirmation_mot_de_passe'] = 'wrongpassword'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirmation_mot_de_passe', response.data)
    
    def test_3_registration_weak_password(self):
        """Test 3: Mot de passe trop faible"""
        data = self.valid_user_data.copy()
        data['mot_de_passe'] = '123'
        data['confirmation_mot_de_passe'] = '123'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('mot_de_passe', response.data)
    
    def test_4_registration_duplicate_username(self):
        """Test 4: Nom d'utilisateur déjà pris"""
        # Premier enregistrement
        self.client.post(self.register_url, self.valid_user_data, format='json')
        
        # Deuxième avec même username
        data = self.valid_user_data.copy()
        data['email'] = 'autre@test.com'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('nom_utilisateur', response.data)
    
    def test_5_login_success(self):
        """Test 5: Connexion réussie"""
        # Créer utilisateur
        self.client.post(self.register_url, self.valid_user_data, format='json')
        
        # Login
        login_data = {
            'nom_utilisateur': 'nouvelutilisateur',
            'mot_de_passe': 'TestPass123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['nom_utilisateur'], 'nouvelutilisateur')
    
    def test_6_login_wrong_password(self):
        """Test 6: Mauvais mot de passe"""
        # Créer utilisateur
        self.client.post(self.register_url, self.valid_user_data, format='json')
        
        # Mauvais mot de passe
        login_data = {
            'nom_utilisateur': 'nouvelutilisateur',
            'mot_de_passe': 'wrongpass'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_7_login_account_locked(self):
        """Test 7: Compte verrouillé après 5 tentatives"""
        # Créer utilisateur
        self.client.post(self.register_url, self.valid_user_data, format='json')
        
        # 5 tentatives échouées
        login_data = {
            'nom_utilisateur': 'nouvelutilisateur',
            'mot_de_passe': 'wrongpass'
        }
        
        for i in range(5):
            response = self.client.post(self.login_url, login_data, format='json')
            if i < 4:
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 6ème tentative - compte verrouillé
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('verrouillé', str(response.data).lower())
    
    def test_8_authenticated_endpoint(self):
        """Test 8: Accès endpoint protégé"""
        # Créer et connecter
        reg_response = self.client.post(self.register_url, self.valid_user_data, format='json')
        token = reg_response.data['access']
        
        # Accéder à /me/
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.valid_user_data['email'])
    
    def test_9_change_password(self):
        """Test 9: Changement de mot de passe"""
        # Créer et connecter
        reg_response = self.client.post(self.register_url, self.valid_user_data, format='json')
        token = reg_response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Changer mot de passe
        password_data = {
            'old_password': 'TestPass123!',
            'new_password': 'NewPass123!',
            'confirm_password': 'NewPass123!'
        }
        response = self.client.post(self.change_password_url, password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Tester nouveau mot de passe
        self.client.credentials()  # Enlever token
        login_data = {
            'nom_utilisateur': 'nouvelutilisateur',
            'mot_de_passe': 'NewPass123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_10_invalid_token(self):
        """Test 10: Token invalide"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken123')
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserPermissionsTests(APITestCase):
    """Tests des permissions"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Créer différents types d'utilisateurs
        self.user = User.objects.create_user(
            username='normaluser',
            email='user@test.com',
            password='UserPass123!',
            role='user'
        )
        
        self.mairie = User.objects.create_user(
            username='mairie',
            email='mairie@test.com',
            password='MairiePass123!',
            role='mairie',
            is_staff=True
        )
        
        self.super_admin = User.objects.create_user(
            username='superadmin',
            email='super@test.com',
            password='SuperPass123!',
            role='super_admin',
            is_staff=True,
            is_superuser=True
        )
    
    def test_user_cannot_create_admin(self):
        """Test: User normal ne peut pas créer d'admin"""
        # Login user normal
        login_data = {'nom_utilisateur': 'normaluser', 'mot_de_passe': 'UserPass123!'}
        response = self.client.post(reverse('login'), login_data, format='json')
        token = response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Tenter création admin
        admin_data = {
            'nom_utilisateur': 'newadmin',
            'email': 'newadmin@test.com',
            'mot_de_passe': 'AdminPass123!',
            'confirmation_mot_de_passe': 'AdminPass123!',
            'nom': 'New',
            'prenom': 'Admin',
            'telephone': '+243123456789',
            'role': 'mairie'
        }
        response = self.client.post(reverse('create-admin'), admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_mairie_cannot_create_admin(self):
        """Test: Mairie ne peut pas créer d'admin"""
        # Login mairie
        login_data = {'nom_utilisateur': 'mairie', 'mot_de_passe': 'MairiePass123!'}
        response = self.client.post(reverse('login'), login_data, format='json')
        token = response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Tenter création admin
        admin_data = {
            'nom_utilisateur': 'newadmin',
            'email': 'newadmin@test.com',
            'mot_de_passe': 'AdminPass123!',
            'confirmation_mot_de_passe': 'AdminPass123!',
            'nom': 'New',
            'prenom': 'Admin',
            'telephone': '+243123456789',
            'role': 'mairie'
        }
        response = self.client.post(reverse('create-admin'), admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_super_admin_can_create_admin(self):
        """Test: Super admin peut créer admin"""
        # Login super admin
        login_data = {'nom_utilisateur': 'superadmin', 'mot_de_passe': 'SuperPass123!'}
        response = self.client.post(reverse('login'), login_data, format='json')
        token = response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Créer admin
        admin_data = {
            'nom_utilisateur': 'newadmin',
            'email': 'newadmin@test.com',
            'mot_de_passe': 'AdminPass123!',
            'confirmation_mot_de_passe': 'AdminPass123!',
            'nom': 'New',
            'prenom': 'Admin',
            'telephone': '+243123456789',
            'role': 'mairie'
        }
        response = self.client.post(reverse('create-admin'), admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
