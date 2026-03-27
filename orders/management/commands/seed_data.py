from django.core.management.base import BaseCommand
from decimal import Decimal
import random
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone

from orders.models import Good, Category, PromoCode


User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        username = "admin"
        email = "admin@example.com"
        password = "admin"

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS("Superuser created"))
        else:
            self.stdout.write("Superuser already exists")

        for i in range(5):
            User.objects.get_or_create(
                username=f"user{i}",
                defaults={"email": f"user{i}@example.com"}
            )

        categories = []
        for name in ["Food", "Electronics", "Books"]:
            category, _ = Category.objects.get_or_create(name=name)
            categories.append(category)

        for i in range(10):
            Good.objects.get_or_create(
                name=f"Good {i}",
                defaults={
                    "price": Decimal(random.randint(10, 500)),
                    "category": random.choice(categories),
                    "is_excluded_from_promotions": random.choice([True, False]),
                }
            )

        now = timezone.now()

        for i in range(3):
            PromoCode.objects.get_or_create(
                code=f"PROMO{i}",
                defaults={
                    "description": f"Promo {i}",
                    "discount": Decimal("0.10") * (i + 1),
                    "category": random.choice(categories),
                    "max_uses": 100,
                    "current_uses": 0,
                    "valid_from": now - timedelta(days=1),
                    "valid_until": now + timedelta(days=30),
                }
            )

        PromoCode.objects.get_or_create(
            code="EXPIRED",
            defaults={
                "description": "Expired promo",
                "discount": Decimal("0.50"),
                "category": random.choice(categories),
                "max_uses": 10,
                "current_uses": 0,
                "valid_from": now - timedelta(days=30),
                "valid_until": now - timedelta(days=1),
            }
        )

        self.stdout.write(self.style.SUCCESS("Demo data created successfully"))