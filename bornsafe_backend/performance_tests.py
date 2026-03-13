from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from .models import ActeNaissance
from provinces.models import Province
import time
from datetime import date, timedelta

User = get_user_model()

class PerformanceTests(APITestCase):
    """Tests de performance"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Créer admin
        self.admin = User.objects.create_user(
            username='admin',
            password='AdminPass123!',
            role='super_admin',
            is_staff=True
        )
        
        # Login
        login_data = {'nom_utilisateur': 'admin', 'mot_de_passe': 'AdminPass123!'}
        response = self.client.post(reverse('login'), login_data, format='json')
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Créer province
        self.province = Province.objects.create(name='Kinshasa')
        
        # Créer beaucoup d'actes pour tester performances
        self.create_bulk_actes(100)
    
    def create_bulk_actes(self, count):
        """Crée plusieurs actes rapidement"""
        actes = []
        for i in range(count):
            actes.append(ActeNaissance(
                numero_acte=f'PERF{i:05d}',
                nom=f'TestNom{i}',
                prenom=f'TestPrenom{i}',
                date_naissance=date(1990, 1, 1) + timedelta(days=i),
                lieu_naissance='Kinshasa',
                province=self.province,
                created_by=self.admin,
                modified_by=self.admin
            ))
        
        ActeNaissance.objects.bulk_create(actes)
    
    def test_list_performance(self):
        """Test performance de la liste"""
        start_time = time.time()
        
        response = self.client.get('/api/actes/')
        
        duration = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(duration, 1.0, f"Trop lent: {duration:.2f}s")
        
        print(f"⏱️  Liste actes: {duration:.3f}s")
    
    def test_search_performance(self):
        """Test performance de la recherche"""
        # Recherche textuelle
        start_time = time.time()
        response = self.client.get('/api/actes/?search=TestNom50')
        duration = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(duration, 0.5, f"Recherche trop lente: {duration:.2f}s")
        print(f"⏱️  Recherche: {duration:.3f}s")
    
    def test_filter_performance(self):
        """Test performance des filtres"""
        start_time = time.time()
        response = self.client.get(f'/api/actes/?province={self.province.id}')
        duration = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(duration, 0.5, f"Filtre trop lent: {duration:.2f}s")
        print(f"⏱️  Filtre: {duration:.3f}s")
    
    def test_detail_performance(self):
        """Test performance de récupération d'un détail"""
        acte = ActeNaissance.objects.first()
        
        start_time = time.time()
        response = self.client.get(f'/api/actes/{acte.id}/')
        duration = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(duration, 0.2, f"Détail trop lent: {duration:.2f}s")
        print(f"⏱️  Détail acte: {duration:.3f}s")
    
    def test_create_performance(self):
        """Test performance de création"""
        data = {
            'numero_acte': 'NEWACTE001',
            'nom': 'Performance',
            'prenom': 'Test',
            'date_naissance': '2000-01-01',
            'lieu_naissance': 'Kinshasa',
            'province_id': self.province.id
        }
        
        start_time = time.time()
        response = self.client.post('/api/actes/', data, format='json')
        duration = time.time() - start_time
        
        self.assertEqual(response.status_code, 201)
        self.assertLess(duration, 0.5, f"Création trop lente: {duration:.2f}s")
        print(f"⏱️  Création acte: {duration:.3f}s")
    
    def test_concurrent_requests(self):
        """Simulation de requêtes concurrentes"""
        import threading
        
        results = []
        
        def make_request():
            response = self.client.get('/api/actes/')
            results.append(response.status_code)
        
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        self.assertEqual(len(results), 10)
        self.assertTrue(all(r == 200 for r in results))
        print("✅ 10 requêtes concurrentes OK")
    
    def test_pagination_performance(self):
        """Test performance avec différentes tailles de page"""
        page_sizes = [10, 20, 50, 100]
        
        for size in page_sizes:
            start_time = time.time()
            response = self.client.get(f'/api/actes/?page_size={size}')
            duration = time.time() - start_time
            
            self.assertEqual(response.status_code, 200)
            self.assertLess(duration, 0.5, f"Page size {size} trop lent: {duration:.2f}s")
            print(f"⏱️  Page size {size}: {duration:.3f}s")
