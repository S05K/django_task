from decimal import Decimal
import json
from django.db import models
from django.forms import JSONField
from my_app.models import CustomUser
import uuid


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='categories/')
    thumbnail = models.ImageField(upload_to='categories/thumbnails/')

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    parent_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    image = models.ImageField(upload_to='subcategories/')
    thumbnail = models.ImageField(upload_to='subcategories/thumbnails/')

    def __str__(self):
        return f"{self.name} - {self.parent_category.name}"


class Size(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price_multiplier = models.DecimalField(max_digits=5, decimal_places=2, help_text="Multiplier for base price")

    def __str__(self):
        return self.name

class Printing(models.Model):
    quality = models.CharField(max_length=100, unique=True)
    price_multiplier = models.DecimalField(max_digits=5, decimal_places=2, help_text="Multiplier for base price")

    def __str__(self):
        return self.quality

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base price before options")
    minimum_qty = models.PositiveIntegerField(default=1, help_text="Minimum quantity for an order")
    qty_step_count = models.PositiveIntegerField(default=1, help_text="Step count for ordering in multiples")
    vat_percent = models.FloatField(default=0.0, help_text="VAT percentage applied")
    
    # Pamphlet customization fields
    options = models.JSONField(default=dict, blank=True, help_text="Customization options (e.g., text, colors, numbers)")
    additional_design_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text="Additional charge for custom design")
    image_description = models.TextField(blank=True, null=True, help_text="Description for images related to this product")
    delivery_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text="Delivery charges for this product")

    def set_options(self, options_dict):
        """ Save dictionary as JSON string """
        self.options = json.dumps(options_dict)

    def get_options(self):
        """ Convert stored JSON string back to dictionary """
        try:
            return json.loads(self.options)
        except (json.JSONDecodeError, TypeError):
            return {}


    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    file_option = models.CharField(max_length=20, choices=[("online", "Attach file Online"), ("email", "Send file via Email")], null=True)
    special_remark = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        """Calculate total price based on size, printing, and quantity."""
        return (self.product.base_price * self.size.price_multiplier * self.printing.price_multiplier) * self.quantity

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class ProductImage(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/images/")
    thumbnail = models.ImageField(upload_to="products/thumbnails/")

    def __str__(self):
        return f"Image for {self.product.name}"

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="cart")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
    printing = models.ForeignKey('Printing', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        """Ensure multiplication works properly."""
        breakpoint()
        if self.product and self.size and self.printing:
            return (self.product.base_price) * Decimal(self.size.price_multiplier) * Decimal(self.printing.price_multiplier) * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} - {self.user.username}"



