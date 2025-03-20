from django.db import models
from my_app.models import CustomUser
from product.models import Product

# Create your models here.
class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="orders")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders")
    quantity = models.PositiveIntegerField()
    options = models.JSONField(default=dict, blank=True, help_text="User's custom options")
    shipping_address = models.JSONField(help_text="Shipping address details")
    billing_address = models.JSONField(help_text="Billing address details")
    files = models.JSONField(default=list, blank=True, help_text="Uploaded files (e.g., design/logo)")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
