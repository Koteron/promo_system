import logging

from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

from orders.models import Good, PromoCode, PromoCodeUsage
from orders.exceptions import (
    PromoCodeNotFoundError,
    PromoCodeExpiredError,
    PromoCodeNotActiveError,
    PromoCodeMaxUsesExceededError,
    PromoCodeAlreadyUsedByUserError,
)


logger = logging.getLogger(__name__)
User = get_user_model()

def validate_promo_code(promo_code_str: str, user: AbstractUser) -> PromoCode:
    try:
        promo_code = PromoCode.objects.get(code=promo_code_str)
    except PromoCode.DoesNotExist:
        logger.warning(f"Promo code '{promo_code_str}' not found")
        raise PromoCodeNotFoundError()
    
    if promo_code.is_expired:
        logger.warning(f"Promo code '{promo_code_str}' is expired")
        raise PromoCodeExpiredError()
    
    now = timezone.now()
    if now < promo_code.valid_from:
        logger.warning(f"Promo code '{promo_code_str}' is not yet valid")
        raise PromoCodeExpiredError(detail="Promo code is not yet valid.")
    
    if promo_code.current_uses >= promo_code.max_uses:
        logger.warning(f"Promo code '{promo_code_str}' has reached max uses")
        raise PromoCodeMaxUsesExceededError()
    
    if PromoCodeUsage.objects.filter(promo_code=promo_code, user=user).exists():
        logger.warning(f"User {user.id} has already used promo code '{promo_code_str}'")
        raise PromoCodeAlreadyUsedByUserError()
    
    logger.info(f"Promo code '{promo_code_str}' validated successfully for user {user.id}")
    return promo_code

def is_promo_applicable_to_good(promo_code: PromoCode, good: Good) -> bool:
    if good.is_excluded_from_promotions:
        return False
    
    if not promo_code.category:
        return True
    
    return good.category == promo_code.category

def promo_code_format_validator(value: str):
    if not value:
        return
    
    if len(value.strip()) == 0:
        raise serializers.ValidationError("Promo code cannot be empty.")
    
    if len(value.strip()) > 50:
        raise serializers.ValidationError("Promo code is too long (max 50 characters).")
    
    if not value.replace('_', '').isalnum():
        raise serializers.ValidationError("Promo code can only contain alphanumeric characters and underscores.")
