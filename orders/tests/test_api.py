from rest_framework.test import APIClient
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from orders.tests.conftest import BaseTestCase
from orders.models import PromoCode


class CreateOrderAPITests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.client = APIClient()

        self.promo = PromoCode.objects.create(
            code="PROMO10",
            discount=Decimal("0.10"),
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=1),
            max_uses=10,
            current_uses=0,
            category=self.category
        )

    def test_api_create_order_success(self):
        payload = {
            "user_id": self.user.id,
            "goods": [
                {"good_id": self.good.id, "quantity": 2}
            ],
            "promo_code": self.promo.code
        }

        response = self.client.post("/api/orders/create/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertIn("order_id", response.data)
        self.assertEqual(len(response.data["goods"]), 1)

    def test_api_missing_goods(self):
        payload = {
            "user_id": self.user.id,
            "goods": []
        }

        response = self.client.post("/api/orders/create/", payload, format="json")
        self.assertEqual(response.status_code, 400)

    def test_api_invalid_promo_code_format(self):
        payload = {
            "user_id": self.user.id,
            "goods": [{"good_id": self.good.id, "quantity": 1}],
            "promo_code": "!!!invalid"
        }

        response = self.client.post("/api/orders/create/", payload, format="json")
        self.assertEqual(response.status_code, 400)