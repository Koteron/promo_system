import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

import orders.services as order_service
from orders.serializers import CreateOrderRequestSerializer, CreateOrderResponseSerializer


logger = logging.getLogger(__name__)


class CreateOrderView(APIView):
    @extend_schema(request=CreateOrderRequestSerializer, responses=CreateOrderResponseSerializer)
    def post(self, request):
        serializer = CreateOrderRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        user_id = validated_data['user_id']
        goods = validated_data['goods']
        promo_code = validated_data.get('promo_code', '').strip() or None
        
        logger.info(f"Creating order for user {user_id} with {len(goods)} items")
        
        order = order_service.create_order(
            user_id=user_id,
            items_data=goods,
            promo_code_str=promo_code,
        )
        
        response_serializer = CreateOrderResponseSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
