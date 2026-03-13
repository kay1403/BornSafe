from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from .models import ActeNaissance
from provinces.models import Province
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
from PIL import Image
import io

User = get_user_model()

class ActeNaissanceModelTests(TestCase):
    """Tests pour le modèle ActeNaissance"""
    
    def setUp(self):
        self.province = Province.objects.create(name='Kinshasa')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.acte = ActeNaissance.objects.create(
            numero_acte='ACTE001',
            nom='Dupont',
            prenom='Jean',
            date_naissance=date(1990, 1, 1),
            lieu_naissance='Kinshasa',
            province=self.province,
            created_by=self.user,
            modified_by=self.user
        )
    
    def test_acte_creation(self):
        """Test création acte"""
        self.assertEqual(self.acte.numero_acte, 'ACTE001')
        self.assertEqual(self.acte.nom, 'Dupont')
        self.assertEqual(self.acte.prenom, 'Jean')
        self.assertEqual(self.acte.status, 'brouillon')
    
    def test_acte_str_method(self):
        """Test méthode __str__"""
        expected = "ACTE001 - Dupont Jean"
        self.assertEqual(str(self.acte), expected)
    
    def test_acte_unique_numero(self):
        """Test unicité numéro d'acte"""
        with self.assertRaises(Exception):
            ActeNaissance.objects.create(
                numero_acte='ACTE001',  # Déjà existant
                nom='Martin',
                prenom='Pierre',
                date_naissance=date(1990, 1, 1),
                lieu_naissance='Kinshasa',
                province=self.province,
                created_by=self.user,
                modified_by=self.user
            )
    
    def test_qr_data_generation(self):
        """Test génération données QR"""
        qr_data = self.acte.get_qr_data()
        self.assertIn('ACTE001', qr_data)
        self.assertIn('Dupont', qr_data)
        self.assertIn('Jean', qr_data)


class ActeNaissanceAPITests(APITestCase):
    """Tests API pour Actes de naissance"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Créer province
        self.province = Province.objects.create(name='Kinshasa')
        
        # Créer utilisateurs
        self.user = User.objects.create_user(
            username='normaluser',
            password='UserPass123!',
            role='user',
            email='user@test.com'
        )
        
        self.mairie = User.objects.create_user(
            username='mairie',
            password='MairiePass123!',
            role='mairie',
            is_staff=True,
            email='mairie@test.com'
        )
        
        self.super_admin = User.objects.create_user(
            username='superadmin',
            password='SuperPass123!',
            role='super_admin',
            is_staff=True,
            is_superuser=True,
            email='super@test.com'
        )
        
        # Créer quelques actes
        self.acte1 = ActeNaissance.objects.create(
            numero_acte='ACTE2025001',
            nom='Dupont',
            prenom='Jean',
            date_naissance=date(1990, 1, 1),
            lieu_naissance='Kinshasa',
            province=self.province,
            created_by=self.mairie,
            modified_by=self.mairie,
            status='valide'
        )
        
        self.acte2 = ActeNaissance.objects.create(
            numero_acte='ACTE2025002',
            nom='Martin',
            prenom='Marie',
            date_naissance=date(1995, 5, 5),
            lieu_naissance='Kinshasa',
            province=self.province,
            created_by=self.mairie,
            modified_by=self.mairie,
            status='brouillon'
        )
        
        self.actes_url = reverse('acte-list')
    
    def login_as(self, user, password):
        """Helper pour login"""
        login_data = {'nom_utilisateur': user.username, 'mot_de_passe': password}
        response = self.client.post(reverse('login'), login_data, format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return token
    
    def test_1_list_actes_as_user(self):
        """Test 1: User voit seulement actes validés"""
        self.login_as(self.user, 'UserPass123!')
        
        response = self.client.get(self.actes_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Ne devrait voir que l'acte validé
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['numero_acte'], 'ACTE2025001')
    
    def test_2_list_actes_as_mairie(self):
        """Test 2: Mairie voit tous ses actes"""
        self.login_as(self.mairie, 'MairiePass123!')
        
        response = self.client.get(self.actes_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Devrait voir ses 2 actes
        self.assertEqual(len(response.data['results']), 2)
    
    def test_3_create_acte_as_user(self):
        """Test 3: User ne peut pas créer d'acte"""
        self.login_as(self.user, 'UserPass123!')
        
        data = {
            'numero_acte': 'ACTE2025003',
            'nom': 'Test',
            'prenom': 'User',
            'date_naissance': '2000-01-01',
            'lieu_naissance': 'Kinshasa',
            'province_id': self.province.id
        }
        
        response = self.client.post(self.actes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_4_create_acte_as_mairie(self):
        """Test 4: Mairie peut créer un acte"""
        self.login_as(self.mairie, 'MairiePass123!')
        
        data = {
            'numero_acte': 'ACTE2025003',
            'nom': 'Test',
            'prenom': 'Creation',
            'date_naissance': '2000-01-01',
            'lieu_naissance': 'Kinshasa',
            'province_id': self.province.id
        }
        
        response = self.client.post(self.actes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérifier création
        self.assertEqual(ActeNaissance.objects.count(), 3)
        acte = ActeNaissance.objects.get(numero_acte='ACTE2025003')
        self.assertEqual(acte.created_by, self.mairie)
        self.assertEqual(acte.status, 'brouillon')
    
    def test_5_create_acte_duplicate_numero(self):
        """Test 5: Impossible de créer avec numéro existant"""
        self.login_as(self.mairie, 'MairiePass123!')
        
        data = {
            'numero_acte': 'ACTE2025001',  # Déjà existant
            'nom': 'Test',
            'prenom': 'Duplicate',
            'date_naissance': '2000-01-01',
            'lieu_naissance': 'Kinshasa',
            'province_id': self.province.id
        }
        
        response = self.client.post(self.actes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('numero_acte', response.data)
    
    def test_6_create_acte_future_date(self):
        """Test 6: Date de naissance future impossible"""
        self.login_as(self.mairie, 'MairiePass123!')
        
        future_date = (timezone.now().date() + timedelta(days=365)).isoformat()
        
        data = {
            'numero_acte': 'ACTE2025004',
            'nom': 'Test',
            'prenom': 'Future',
            'date_naissance': future_date,
            'lieu_naissance': 'Kinshasa',
            'province_id': self.province.id
        }
        
        response = self.client.post(self.actes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_7_update_acte_as_creator(self):
        """Test 7: Mairie peut modifier son acte"""
        self.login_as(self.mairie, 'MairiePass123!')
        
        url = reverse('acte-detail', args=[self.acte2.id])
        data = {'nom': 'Martin-Modifié'}
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.acte2.refresh_from_db()
        self.assertEqual(self.acte2.nom, 'Martin-Modifié')
    
    def test_8_validate_acte(self):
        """Test 8: Valider un acte"""
        self.login_as(self.mairie, 'MairiePass123!')
        
        url = reverse('acte-validate', args=[self.acte2.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.acte2.refresh_from_db()
        self.assertEqual(self.acte2.status, 'valide')
    
    def test_9_verify_acte(self):
        """Test 9: Vérifier un acte"""
        self.login_as(self.user, 'UserPass123!')
        
        url = reverse('acte-verify')
        data = {
            'numero_acte': 'ACTE2025001',
            'nom': 'Dupont',
            'prenom': 'Jean',
            'date_naissance': '1990-01-01',
            'lieu_naissance': 'Kinshasa',
            'province_id': self.province.id
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'conforme')
    
    def test_10_verify_invalid_acte(self):
        """Test 10: Vérifier acte invalide"""
        self.login_as(self.user, 'UserPass123!')
        
        url = reverse('acte-verify')
        data = {
            'numero_acte': 'INVALID',
            'nom': 'Inconnu',
            'prenom': 'Personne',
            'date_naissance': '1990-01-01',
            'lieu_naissance': 'Kinshasa',
            'province_id': self.province.id
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_11_search_actes(self):
        """Test 11: Recherche d'actes"""
        self.login_as(self.mairie, 'MairiePass123!')
        
        # Recherche par nom
        response = self.client.get(f"{self.actes_url}?search=Dupont")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Recherche par numéro
        response = self.client.get(f"{self.actes_url}?search=ACTE2025002")
        self.assertEqual(len(response.data['results']), 1)
    
    def test_12_filter_by_status(self):
        """Test 12: Filtre par statut"""
        self.login_as(self.mairie, 'MairiePass123!')
        
        response = self.client.get(f"{self.actes_url}?status=valide")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'valide')
    
    def test_13_download_pdf(self):
        """Test 13: Téléchargement PDF"""
        self.login_as(self.user, 'UserPass123!')
        
        url = reverse('acte-download-pdf', args=[self.acte1.id])
        response = self.client.get(url)
        
        # Devrait générer un PDF à la volée
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
    
    def test_14_qr_code_generation(self):
        """Test 14: Génération QR code"""
        self.login_as(self.mairie, 'MairiePass123!')
        
        # Vérifier que le QR code est généré après validation
        url = reverse('acte-validate', args=[self.acte2.id])
        response = self.client.post(url)
        
        self.acte2.refresh_from_db()
        self.assertIsNotNone(self.acte2.qr_code)
    
    def test_15_pagination(self):
        """Test 15: Pagination fonctionne"""
        self.login_as(self.mairie, 'MairiePass123!')
        
        # Créer plusieurs actes
        for i in range(15):
            ActeNaissance.objects.create(
                numero_acte=f'ACTE2025{i+10:03d}',
                nom=f'Test{i}',
                prenom='Pagination',
                date_naissance=date(2000, 1, 1),
                lieu_naissance='Kinshasa',
                province=self.province,
                created_by=self.mairie,
                modified_by=self.mairie
            )
        
        response = self.client.get(self.actes_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier pagination (page_size=20 par défaut)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
