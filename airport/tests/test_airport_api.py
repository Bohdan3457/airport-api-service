from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport

AIRPORT_URL = reverse("airport:airport-list")


class UnauthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_not_required_for_list(self):
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class AuthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="user@test.com",
            password="testpassword123",
        )
        self.client.force_authenticate(self.user)

    def test_create_airport_forbidden_for_regular_user(self):
        payload = {
            "name": "Boryspil",
            "closest_big_city": "Kyiv",
        }
        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            username="adminuser",
            email="admin@test.com",
            password="testpassword123",
        )
        self.client.force_authenticate(self.user)

    def test_create_airport_allowed_for_admin(self):
        payload = {
            "name": "Boryspil",
            "closest_big_city": "Kyiv",
        }
        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        airport = Airport.objects.get(id=res.data["id"])
        self.assertEqual(airport.name, payload["name"])
