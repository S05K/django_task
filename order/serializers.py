from decimal import Decimal
from rest_framework import serializers
from .models import Order, Product

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

    def validate(self, data):
        product = data.get("product")
        quantity = data.get("quantity")

        # Ensure quantity is at least the minimum required
        if quantity < product.minimum_qty or quantity % product.qty_step_count != 0:
            raise serializers.ValidationError("Quantity must be at least the minimum and in step count multiples.")

        return data

    def create(self, validated_data):
        product = validated_data["product"]
        quantity = validated_data["quantity"]
        user_options = validated_data["options"]

        # Convert vat_percent to Decimal
        vat_percent = Decimal(product.vat_percent)  

        # Calculate total price
        base_price = product.base_price * quantity
        design_charge = product.additional_design_charge * quantity
        vat = (vat_percent / 100) * base_price
        total_price = base_price + design_charge + product.delivery_charges + vat

        # Process user_options if they impact the price
        customization_charge = Decimal("0.00")
        for option in user_options:
            if option.get("value"):  # If there's a valid user input
                customization_charge += Decimal("1.00")  # Example charge per customization

        total_price += customization_charge  # Add customization charge

        validated_data["total_amount"] = total_price
        return super().create(validated_data)

