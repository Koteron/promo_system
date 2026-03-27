from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from orders.tests.conftest import BaseTestCase
from orders.services import create_order
from orders.exceptions import (
    UserNotFoundError,
    InvalidOrderDataError,
)
from orders.models import PromoCode, Good, Category


class CreateOrderTests(BaseTestCase):

    def setUp(self):
        super().setUp()

        self.promo = PromoCode.objects.create(
            code="PROMO10",
            discount=Decimal("0.10"),
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=1),
            max_uses=10,
            current_uses=0,
            category=self.category
        )

    def test_create_order_without_promo(self):
        order = create_order(
            user_id=self.user.id,
            items_data=[{"good_id": self.good.id, "quantity": 2}]
        )

        self.assertEqual(order.total_price, Decimal("2000.00"))
        self.assertEqual(order.final_price, Decimal("2000.00"))
        self.assertEqual(order.items.count(), 1)

    def test_create_order_with_promo(self):
        order = create_order(
            user_id=self.user.id,
            items_data=[{"good_id": self.good.id, "quantity": 1}],
            promo_code_str=self.promo.code
        )

        self.assertEqual(order.total_price, Decimal("1000.00"))
        self.assertEqual(order.final_price, Decimal("900.00"))

    def test_promo_not_applied_to_excluded_goods(self):
        order = create_order(
            user_id=self.user.id,
            items_data=[{"good_id": self.excluded_good.id, "quantity": 1}],
            promo_code_str=self.promo.code
        )

        self.assertEqual(order.final_price, Decimal("500.00"))

    def test_promo_category_restriction(self):
        other_category = Category.objects.create(name="Books")

        other_good = Good.objects.create(
            name="Book",
            category=other_category,
            price=Decimal("100.00")
        )

        order = create_order(
            user_id=self.user.id,
            items_data=[{"good_id": other_good.id, "quantity": 1}],
            promo_code_str=self.promo.code
        )

        self.assertEqual(order.final_price, Decimal("100.00"))

    def test_invalid_user(self):
        with self.assertRaises(UserNotFoundError):
            create_order(
                user_id=9999,
                items_data=[{"good_id": self.good.id, "quantity": 1}]
            )

    def test_invalid_good(self):
        with self.assertRaises(InvalidOrderDataError):
            create_order(
                user_id=self.user.id,
                items_data=[{"good_id": 9999, "quantity": 1}]
            )