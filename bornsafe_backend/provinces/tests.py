from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Province

User = get_user_model()

class ProvinceAPITestCase(TestCase):
    def setUp(self):
        # Création utilisateurs
        self.admin_user = User.objects.create_user(username="admin", password="admin123", is_staff=True)
        self.normal_user = User.objects.create_user(username="user", password="user123", is_staff=False)

        # Création client API
        self.client = APIClient()

        # Création d'une province
        self.province = Province.objects.create(nom="Gabon")

    def test_list_provinces_user(self):
        self.client.login(username="user", password="user123")
        response = self.client.get("/api/provinces/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nom'], "Gabon")

    def test_create_province_admin(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.post("/api/provinces/", {"nom": "Libreville"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Province.objects.count(), 2)

    def test_create_province_non_admin(self):
        self.client.login(username="user", password="user123")
        response = self.client.post("/api/provinces/", {"nom": "Port-Gentil"})
        self.assertEqual(response.status_code, 403)  # interdit pour user normal
