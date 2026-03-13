from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

User = get_user_model()

class UserModelTests(TestCase):
    """Tests pour le modèle User"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_create_user(self):
        """Test la création d'un utilisateur"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@test.com')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertEqual(self.user.role, 'user')
        self.assertFalse(self.user.is_staff)
    
    def test_create_superuser(self):
        """Test la création d'un super utilisateur"""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
    
    def test_failed_login_tracking(self):
        """Test le suivi des tentatives de connexion échouées"""
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.user.record_failed_login()
        self.assertEqual(self.user.failed_login_attempts, 1)
        
        # Verrouillage après 5 tentatives
        for i in range(4):
            self.user.record_failed_login()
        self.assertTrue(self.user.is_account_locked())
        
        # Réinitialisation
        self.user.reset_failed_login_attempts()
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.assertFalse(self.user.is_account_locked())


class UserAPITests(APITestCase):
    """Tests pour l'API User"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        
        self.user_data = {
            'nom_utilisateur': 'newuser',
            'email': 'newuser@test.com',
            'mot_de_passe': 'TestPass123!',
            'confirmation_mot_de_passe': 'TestPass123!',
            'nom': 'New',
            'prenom': 'User',
            'telephone': '+243123456789'
        }
    
    def test_user_registration(self):
        """Test l'enregistrement d'un utilisateur"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], self.user_data['email'])
    
    def test_user_registration_password_mismatch(self):
        """Test la validation des mots de passe"""
        data = self.user_data.copy()
        data['confirmation_mot_de_passe'] = 'wrongpassword'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login(self):
        """Test la connexion utilisateur"""
        # Créer d'abord un utilisateur
        self.client.post(self.register_url, self.user_data, format='json')
        
        # Tenter la connexion
        login_data = {
            'nom_utilisateur': 'newuser',
            'mot_de_passe': 'TestPass123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_user_login_wrong_password(self):
        """Test connexion avec mauvais mot de passe"""
        # Créer un utilisateur
        self.client.post(self.register_url, self.user_data, format='json')
        
        # Mauvais mot de passe
        login_data = {
            'nom_utilisateur': 'newuser',
            'mot_de_passe': 'wrongpass'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_authenticated_endpoint(self):
        """Test l'accès à un endpoint protégé"""
        # Créer et connecter un utilisateur
        reg_response = self.client.post(self.register_url, self.user_data, format='json')
        token = reg_response.data['access']
        
        # Accéder à /me/
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email'])
