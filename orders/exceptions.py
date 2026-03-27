from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import status


class OrderException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Order processing error.'
    default_code = 'order_error'


class PromoCodeException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid promo code.'
    default_code = 'promo_code_error'


class PromoCodeNotFoundError(PromoCodeException):
    default_detail = 'Promo code not found.'
    default_code = 'promo_code_not_found'


class PromoCodeExpiredError(PromoCodeException):
    default_detail = 'Promo code has expired.'
    default_code = 'promo_code_expired'


class PromoCodeNotActiveError(PromoCodeException):
    default_detail = 'Promo code is not active.'
    default_code = 'promo_code_not_active'


class PromoCodeMaxUsesExceededError(PromoCodeException):
    default_detail = 'Promo code has reached maximum usage limit.'
    default_code = 'promo_code_max_uses_exceeded'


class PromoCodeAlreadyUsedByUserError(PromoCodeException):
    default_detail = 'You have already used this promo code.'
    default_code = 'promo_code_already_used'


class GoodNotFoundError(OrderException):
    default_detail = 'Good not found.'
    default_code = 'good_not_found'


class UserNotFoundError(OrderException):
    default_detail = 'User not found.'
    default_code = 'user_not_found'


class InvalidOrderDataError(OrderException):
    default_detail = 'Invalid order data.'
    default_code = 'invalid_order_data'


def custom_exception_handler(exc, context):

    response = drf_exception_handler(exc, context)
    
    if response is not None:
        response.data = {
            'error': response.data.get('detail', str(exc)) if isinstance(response.data, dict) else str(exc),
            'code': getattr(exc, 'default_code', 'unknown_error'),
        }
    
    return response
