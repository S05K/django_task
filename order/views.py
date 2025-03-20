from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Order
from .serializers import OrderSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .pagination import OrderPagination

class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            data = request.data
            product_id = data.get("product_id")
            quantity = data.get("quantity")
            options = data.get("options", {})
            shipping_address = data.get("shipping_address")
            billing_address = data.get("billing_address")
            files = data.get("files", [])

            product = get_object_or_404(Product, id=product_id)

            # Validate quantity
            if quantity < product.minimum_qty or quantity % product.qty_step_count != 0:
                return Response({"error": "Invalid quantity. Must be at least minimum quantity and in multiples of step count."}, status=status.HTTP_400_BAD_REQUEST)

            # Calculate total price
            base_price = product.base_price * quantity
            design_charge = product.additional_design_charge * quantity
            vat = (Decimal(str(product.vat_percent)) / Decimal("100")) * base_price
            total_price = base_price + design_charge + product.delivery_charges + vat

            # Save order
            order = Order.objects.create(
                user=user,
                product=product,
                quantity=quantity,
                options=options,
                shipping_address=shipping_address,
                billing_address=billing_address,
                files=files,
                total_amount=total_price
            )

            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get(self, request, order_id):
        user = request.user
        try:
            order = Order.objects.get(id=order_id)

            # If the user is authorized or owns the order, return order details
            if user.is_authorized or order.user.id == user.id:
                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response({"error": "This is not your order. Please enter your order ID."}, status=status.HTTP_403_FORBIDDEN)

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderPaginatedView(APIView):
        permission_classes = [IsAuthenticated]

        def get(self, request):

            try:
                
                # Apply pagination
                paginator = OrderPagination()
                order = Order.objects.all()
                paginated_products = paginator.paginate_queryset(order, request)

                serializer = OrderSerializer(paginated_products, many=True)
                return paginator.get_paginated_response(serializer.data)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
