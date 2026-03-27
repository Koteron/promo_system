from datetime import timedelta
from django.utils import timezone
from decimal import Decimal

from orders.tests.conftest import BaseTestCase
from orders.models import PromoCode, PromoCodeUsage, Order
from orders.exceptions import (
    PromoCodeNotActiveError,
    PromoCodeMaxUsesExceededError,
    PromoCodeAlreadyUsedByUserError,
    PromoCodeExpiredError,
    PromoCodeNotFoundError
)
from orders.services import validate_promo_code


class PromoCodeValidationTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.promo = PromoCode.objects.create(
            code="PROMO10",
            discount=Decimal("0.10"),
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=1),
            max_uses=5,
            current_uses=0,
            category=self.category
        )

    def test_valid_promo_code(self):
        promo = validate_promo_code(self.promo.code, self.user)
        self.assertEqual(promo.id, self.promo.id)

    def test_promo_code_not_found(self):
        with self.assertRaises(PromoCodeNotFoundError):
            validate_promo_code("INVALID", self.user)

    def test_promo_code_expired(self):
        self.promo.valid_until = timezone.now() - timedelta(days=1)
        self.promo.save()

        with self.assertRaises(PromoCodeExpiredError):
            validate_promo_code(self.promo.code, self.user)

    def test_promo_code_not_yet_valid(self):
        self.promo.valid_from = timezone.now() + timedelta(days=1)
        self.promo.save()

        with self.assertRaises(PromoCodeExpiredError):
            validate_promo_code(self.promo.code, self.user)

    def test_promo_code_max_uses_exceeded(self):
        self.promo.current_uses = 5
        self.promo.save()
        
        with self.assertRaises(PromoCodeMaxUsesExceededError):
            validate_promo_code(self.promo.code, self.user)

    def test_user_cannot_reuse_promo_code(self):
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal("1.0"),
            final_price=Decimal("1.0"),
            promo_code=self.promo,
        )
        PromoCodeUsage.objects.create(
            promo_code=self.promo,
            user=self.user,
            order=order,
        )

        with self.assertRaises(PromoCodeAlreadyUsedByUserError):
            validate_promo_code(self.promo.code, self.user)