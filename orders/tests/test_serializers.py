from django.test import TestCase
from orders.serializers import CreateOrderResponseSerializer
from unittest.mock import MagicMock


class SerializerTests(TestCase):

    def test_zero_discount(self):
        order = MagicMock()
        order.total_price = 0
        order.final_total = 0

        serializer = CreateOrderResponseSerializer(order)

        self.assertEqual(serializer.data["discount"], "0.00")