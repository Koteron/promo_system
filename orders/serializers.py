from rest_framework import serializers
from orders.models import OrderItem
from orders.validators import promo_code_format_validator


class OrderItemRequestSerializer(serializers.Serializer):
    good_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class CreateOrderRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(
        min_value=1
    )
    goods = OrderItemRequestSerializer(
        many=True
    )
    promo_code = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=50,
        validators=[promo_code_format_validator],
    )
    
    def validate_goods(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError("At least one good is required.")
        return value


class OrderItemResponseSerializer(serializers.ModelSerializer):
    price_per_unit = serializers.DecimalField(max_digits=12, decimal_places=2)
    discount = serializers.DecimalField(max_digits=5, decimal_places=2)
    total = serializers.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = ['good_id', 'quantity', 'price_per_unit', 'discount', 'total']

class CreateOrderResponseSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(source='user.id')
    order_id = serializers.IntegerField(source='id')
    goods = OrderItemResponseSerializer(many=True, source='items')
    price = serializers.DecimalField(max_digits=12, decimal_places=2, source='total_price')
    discount = serializers.SerializerMethodField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2, source='final_total')

    def get_discount(self, obj):
        if obj.total_price == 0:
            return "0.00"
        discount_percent = (1 - obj.final_total / obj.total_price) * 100
        return f"{discount_percent:.2f}"
