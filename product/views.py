from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, Product, Order, Size, Printing, Category, Subcategory
from .serializers import CartSerializer, OrderSerializer, ProductSerializer, CategorySerializer, SubcategorySerializer
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


class ProductView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class SubcategoryByCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        subcategories = Subcategory.objects.filter(parent_category=category)
        serializer = SubcategorySerializer(subcategories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductBySubcategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, subcategory_id):
        subcategory = get_object_or_404(Subcategory, id=subcategory_id)
        products = Product.objects.filter(subcategory=subcategory)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class ProductDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,product_id):
        product = Product.objects.get(id=product_id)
        serializer = ProductSerializer(product)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all cart items for the logged-in user."""
        cart = Cart.objects.all()
        cart_items = Cart.objects.filter(user=request.user)
        print(cart_items,'---------------')
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Add a product to the cart."""
        product_id = request.data.get("product")
        size_id = request.data.get("size")
        printing_id = request.data.get("printing")
        quantity = int(request.data.get("quantity", 1))

        try:
            product = Product.objects.get(id=product_id)
            size = Size.objects.get(id=size_id) if size_id else None
            printing = Printing.objects.get(id=printing_id) if printing_id else None

            cart_item, created = Cart.objects.get_or_create(
                user=request.user, product=product, size=size, printing=printing,
                defaults={"quantity": quantity}
            )
            if not created:
                cart_item.quantity += quantity  # Update quantity if the item already exists
                cart_item.save()

            serializer = CartSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Size.DoesNotExist:
            return Response({"error": "Size not found"}, status=status.HTTP_404_NOT_FOUND)
        except Printing.DoesNotExist:
            return Response({"error": "Printing option not found"}, status=status.HTTP_404_NOT_FOUND)
        

    def put(self, request, cart_id):
        """Update quantity or product in the cart."""
        try:
            cart_item = Cart.objects.get(id=cart_id, user=request.user)
            
            product_id = request.data.get("product")
            quantity = request.data.get("quantity")

            if product_id:
                try:
                    product = Product.objects.get(id=product_id)
                    cart_item.product = product
                except Product.DoesNotExist:
                    return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

            if quantity is not None:
                try:
                    quantity = quantity
                    if quantity <= 0:
                        return Response({"error": "Quantity must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)
                    cart_item.quantity = quantity
                except ValueError:
                    return Response({"error": "Invalid quantity format"}, status=status.HTTP_400_BAD_REQUEST)

            cart_item.save()
            serializer = CartSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)


    def delete(self, request, cart_id):
        """Remove a product from the cart."""
        try:
            cart_item = Cart.objects.get(id=cart_id, user=request.user)
            cart_item.delete()
            return Response({"message": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return Response({"error": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND)
