from rest_framework import serializers
from django.db import transaction
from decimal import Decimal

from .models import Customer, FoodItem, Order, OrderItem


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderItemInputSerializer(serializers.Serializer):
    food_item = serializers.PrimaryKeyRelatedField(
        queryset=FoodItem.objects.all()
    )
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemInputSerializer(many=True, write_only=True)
    order_items = OrderItemSerializer(
        many=True, read_only=True, source='items'
    )

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'status', 'total_amount',
            'created_at', 'items', 'order_items'
        ]
        read_only_fields = ['total_amount', 'created_at']

    def validate_status(self, value):
        if self.instance is None and value != 'PENDING':
            raise serializers.ValidationError(
                "New orders must have PENDING status."
            )
        return value

    def validate_items(self, items):
        for item in items:
            if not item['food_item'].is_available:
                raise serializers.ValidationError(
                    f"{item['food_item'].name} is unavailable."
                )
        return items

    @transaction.atomic
    def create(self, validated_data):
        items = validated_data.pop('items')

        total = sum(
            (item['food_item'].price * item['quantity']
             for item in items),
            Decimal('0.00')
        )

        order = Order.objects.create(
            total_amount=total,
            **validated_data
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                food_item=item['food_item'],
                quantity=item['quantity'],
                price_at_order=item['food_item'].price
            )

        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        items = validated_data.pop('items', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if items is not None:
            instance.items.all().delete()

            total = Decimal('0.00')

            for item in items:
                food = item['food_item']
                quantity = item['quantity']
                total += food.price * quantity

                OrderItem.objects.create(
                    order=instance,
                    food_item=food,
                    quantity=quantity,
                    price_at_order=food.price
                )

            instance.total_amount = total

        instance.save()
        return instance