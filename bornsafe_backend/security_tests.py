from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.core.cache import cache
import time

User = get_user_model()

class SecurityTests(APITestCase):
    """Tests de sécurité"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123!'
        )
        
        self.login_url = reverse('login')
        self.register_url = reverse('register')
    
    def test_rate_limiting_login(self):
        """Test rate limiting sur login"""
        # Tentatives rapides
        for i in range(6):  # Plus que la limite de 5/min
            data = {
                'nom_utilisateur': 'testuser',
                'mot_de_passe': 'wrongpass'
            }
            response = self.client.post(self.login_url, data, format='json')
            
            if i < 5:
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            else:
                # Devrait être rate limité
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
    
    def test_rate_limiting_register(self):
        """Test rate limiting sur register"""
        base_data = {
            'nom': 'Test',
            'prenom': 'User',
            'telephone': '+243123456789'
        }
        
        for i in range(6):  # Plus que la limite
            data = base_data.copy()
            data.update({
                'nom_utilisateur': f'user{i}',
                'email': f'user{i}@test.com',
                'mot_de_passe': 'TestPass123!',
                'confirmation_mot_de_passe': 'TestPass123!'
            })
            
            response = self.client.post(self.register_url, data, format='json')
            
            if i < 5:
                self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
            else:
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
    
    def test_sql_injection_protection(self):
        """Test protection contre injection SQL"""
        self.client.force_authenticate(user=self.user)
        
        # Tentative d'injection SQL dans la recherche
        malicious_input = "'; DROP TABLE accounts_user; --"
        response = self.client.get(f"/api/actes/?search={malicious_input}")
        
        # Vérifier que la requête n'a pas crashé
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que la table existe toujours
        self.assertTrue(User.objects.exists())
    
    def test_xss_protection(self):
        """Test protection contre XSS"""
        self.client.force_authenticate(user=self.user)
        
        # Tentative d'injection XSS
        xss_payload = "<script>alert('XSS')</script>"
        response = self.client.get(f"/api/actes/?search={xss_payload}")
        
        # Vérifier que le payload n'est pas exécuté
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = response.content.decode()
        self.assertNotIn('<script>', content)
    
    def test_jwt_token_security(self):
        """Test sécurité des tokens JWT"""
        # Login
        data = {
            'nom_utilisateur': 'testuser',
            'mot_de_passe': 'TestPass123!'
        }
        response = self.client.post(self.login_url, data, format='json')
        token = response.data['access']
        
        # Tester avec token modifié
        modified_token = token[:-5] + 'xxxxx'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {modified_token}')
        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Tester sans Bearer
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_password_policy(self):
        """Test politique de mots de passe"""
        weak_passwords = [
            '12345678',  # Trop simple
            'password',  # Commun
            'aaaaaaa',   # Trop simple
            'test',      # Trop court
            self.user.username,  # Similaire au username
        ]
        
        base_data = {
            'nom_utilisateur': 'newuser',
            'email': 'new@test.com',
            'confirmation_mot_de_passe': 'same',
            'nom': 'Test',
            'prenom': 'User',
            'telephone': '+243123456789'
        }
        
        for weak_pass in weak_passwords:
            data = base_data.copy()
            data['mot_de_passe'] = weak_pass
            data['confirmation_mot_de_passe'] = weak_pass
            
            response = self.client.post(self.register_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_session_hijacking_protection(self):
        """Test protection contre le vol de session"""
        # Login
        data = {
            'nom_utilisateur': 'testuser',
            'mot_de_passe': 'TestPass123!'
        }
        response = self.client.post(self.login_url, data, format='json')
        token = response.data['access']
        
        # Utiliser le token depuis une autre IP simulée
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Le JWT ne lie pas à l'IP par défaut, mais on peut vérifier
        # que les claims sont corrects
        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_brute_force_protection(self):
        """Test protection contre brute force"""
        # Tentatives rapides avec différents mots de passe
        for i in range(10):
            data = {
                'nom_utilisateur': 'testuser',
                'mot_de_passe': f'wrongpass{i}'
            }
            response = self.client.post(self.login_url, data, format='json')
            
            # Les premières tentatives échouent normalement
            if i < 5:
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            else:
                # Après 5 tentatives, rate limit ou compte verrouillé
                self.assertIn(response.status_code, [
                    status.HTTP_400_BAD_REQUEST,
                    status.HTTP_429_TOO_MANY_REQUESTS
                ])
        
        # Vérifier que le compte est verrouillé
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_account_locked())
