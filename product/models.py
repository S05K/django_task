from django.db import models
from my_app.models import CustomUser
import uuid

class Size(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    price_multiplier = models.DecimalField(max_digits=5, decimal_places=2, help_text="Multiplier for base price")

    def __str__(self):
        return self.name

class Printing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quality = models.CharField(max_length=100, unique=True)
    price_multiplier = models.DecimalField(max_digits=5, decimal_places=2, help_text="Multiplier for base price")

    def __str__(self):
        return self.quality

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base price before multipliers")

    def __str__(self):
        return self.name

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    printing = models.ForeignKey(Printing, on_delete=models.CASCADE)
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
