from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings
from decimal import Decimal


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categories"
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Good(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='goods')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    is_excluded_from_promotions = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class PromoCode(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))],
    )
    # if set - only to this, if not set - to everything
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='promocodes')
    max_uses = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    current_uses = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'promo_codes'
        verbose_name = 'Promo Code'
        verbose_name_plural = 'Promo Codes'
    
    def __str__(self):
        return self.code
    
    @property
    def is_expired(self):
        return self.valid_until is not None and timezone.now() > self.valid_until
    
    @property
    def is_valid(self):
        if self.is_expired:
            return False
        if self.current_uses >= self.max_uses:
            return False
        now = timezone.now()
        if now < self.valid_from:
            return False
        return True


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING'
        PAID = 'PAID'
        COMPLETED = 'COMPLETED'
        CANCELLED = 'CANCELLED'
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0'))]
    )
    final_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0'))]
    )
    promo_code = models.ForeignKey(
        PromoCode, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"Order #{self.id} - User {self.user.id}"


class PromoCodeUsage(models.Model):
    id = models.AutoField(primary_key=True)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="promo_code_usages")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='promo_code_usage')
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'promo_code_usages'
        verbose_name = 'Promo Code Usage'
        verbose_name_plural = 'Promo Code Usages'
        unique_together = [('promo_code', 'user', 'order')]
    
    def __str__(self):
        return f"{self.promo_code.code} - {self.user.username}"


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    good = models.ForeignKey(Good, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    discount = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0'), 
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))]
    )
    total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0'))]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def __str__(self):
        return f"OrderItem #{self.id} - Order #{self.order.id}"    
