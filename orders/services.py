import logging
from decimal import Decimal
from django.db import transaction
from django.contrib.auth import get_user_model

from orders.validators import validate_promo_code, is_promo_applicable_to_good
from orders.models import (
    Order, 
    OrderItem, 
    Good, 
    PromoCodeUsage
)
from orders.exceptions import (
    UserNotFoundError,
    InvalidOrderDataError,
)


logger = logging.getLogger(__name__)
User = get_user_model()
    

def validate_order_items(items_data: list) -> list:
    if not items_data:
        raise InvalidOrderDataError(detail="Order must contain at least one item.")

    good_ids = [item.get('good_id') for item in items_data]
    if None in good_ids:
        raise InvalidOrderDataError(detail="Each item must have good_id.")

    for item in items_data:
        quantity = item.get('quantity')
        if not isinstance(quantity, int) or quantity <= 0:
            raise InvalidOrderDataError(detail="Quantity must be a positive integer.")

    goods_qs = Good.objects.filter(id__in=good_ids)
    goods_map = {good.id: good for good in goods_qs}

    missing_ids = set(good_ids) - set(goods_map.keys())
    if missing_ids:
        raise InvalidOrderDataError(detail=f"Goods not found: {missing_ids}")

    validated_items = [(goods_map[item['good_id']], item['quantity']) for item in items_data]
    return validated_items

@transaction.atomic
def create_order(user_id: int, items_data: list, promo_code_str: str = None) -> Order:
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        raise UserNotFoundError()
    items = validate_order_items(items_data)

    promo_code = None
    if promo_code_str:
        promo_code = validate_promo_code(promo_code_str, user)

    total_price = Decimal('0')
    discount_amount = Decimal('0')
    order_items_to_create = []

    order = Order.objects.create(
        user=user,
        total_price=total_price,
        final_total=Decimal('0'),
        promo_code=promo_code,
        status=Order.Status.PENDING,
    )

    for good, quantity in items:
        subtotal = good.price * quantity
        total_price += subtotal

        item_discount = Decimal('0')
        if promo_code and is_promo_applicable_to_good(promo_code, good):
            item_discount = subtotal * promo_code.discount
            discount_amount += item_discount

        order_items_to_create.append(
            OrderItem(
                order=order,
                good=good,
                quantity=quantity,
                price_per_unit=good.price,
                discount=promo_code.discount if item_discount else 0.0,
                total=subtotal - item_discount,
            )
        )

    order.total_price = total_price
    order.final_total = total_price - discount_amount

    OrderItem.objects.bulk_create(order_items_to_create)

    if promo_code:
        PromoCodeUsage.objects.create(promo_code=promo_code, user=user, order=order)
        promo_code.current_uses += 1
        promo_code.save(update_fields=['current_uses'])

    return order
