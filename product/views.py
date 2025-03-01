from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Product, Order, Size, Printing
from .serializers import OrderSerializer, ProductSerializer
# Create your views here.

class AllDetailsView(APIView):
    def get(self,request):
        a=Product.objects.first()
        b=Size.objects.first()
        c=Printing.objects.first()
        print([a.id, b.id, c.id])
        return Response({"Hello":"World"})
    



class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]  # Only logged-in users can order

    def post(self, request):
        user = request.user
        product_id = request.data.get("product_id")
        size_id = request.data.get("size_id")
        printing_id = request.data.get("printing_id")
        quantity = request.data.get("quantity")

        # Validating input data
        if not all([product_id, size_id, printing_id, quantity]):
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
            size = Size.objects.get(id=size_id)
            printing = Printing.objects.get(id=printing_id)
            quantity = int(quantity)

            # Create Order
            order = Order.objects.create(
                user=user,
                product=product,
                size=size,
                printing=printing,
                quantity=quantity
            )

            # Serialize the order and return response
            serializer = OrderSerializer(order)
            return Response(
                {
                    "message": "Order placed successfully!",
                    "total_price": order.total_price,  # Fetching from @property
                    "order_details": serializer.data,
                },
                status=status.HTTP_201_CREATED
            )

        except (Product.DoesNotExist, Size.DoesNotExist, Printing.DoesNotExist):
            return Response({"error": "Invalid product, size, or printing option."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Quantity must be a valid number."}, status=status.HTTP_400_BAD_REQUEST)


class CreateProductView(APIView):
    permission_classes = [IsAuthenticated]  # Only logged-in users can access

    def post(self, request):
        user = request.user

        # Check if the user is authorized
        if not user.is_authorized:
            return Response({"error": "You are not authorized to create products."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product created successfully!", "product": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
