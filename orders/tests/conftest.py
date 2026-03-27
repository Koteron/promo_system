from django.test import TestCase
from decimal import Decimal

from orders.models import User, Category, Good


class BaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", email="test@test.com")

        self.category = Category.objects.create(name="Electronics")

        self.good = Good.objects.create(
            name="Laptop",
            category=self.category,
            price=Decimal("1000.00"),
        )

        self.excluded_good = Good.objects.create(
            name="Excluded",
            category=self.category,
            price=Decimal("500.00"),
            is_excluded_from_promotions=True
        )