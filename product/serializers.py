from rest_framework import serializers
from .models import Order, Product, Category, Subcategory, ProductImage, Printing, Size, Cart



class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'thumbnail']

    def get_image(self, obj):
        return obj.image.url if obj.image else None

    def get_thumbnail(self, obj):
        return obj.thumbnail.url if obj.thumbnail else None


class SubcategorySerializer(serializers.ModelSerializer):
    parent_category = CategorySerializer()
    image = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'image', 'thumbnail', 'parent_category']

    def get_image(self, obj):
        return obj.image.url if obj.image else None

    def get_thumbnail(self, obj):
        return obj.thumbnail.url if obj.thumbnail else None

class OrderSerializer(serializers.ModelSerializer):
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ["id", "product", "size", "printing", "quantity", "total_price", "created_at"]

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image", "thumbnail"]

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    subcategory = SubcategorySerializer()
    parent_category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "base_price",'subcategory', 'parent_category', 'images']

    def get_parent_category(self, obj):
        return obj.subcategory.parent_category.name if obj.subcategory else None



class CartSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.base_price', max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'product_name', 'product_price', 'size', 'printing', 'quantity', 'total_price','images', 'added_at']
        read_only_fields = ['total_price']
