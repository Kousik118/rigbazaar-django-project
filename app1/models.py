from django.db import models
from django.contrib.auth.models import AbstractUser


class Account(AbstractUser):
    phone = models.CharField(max_length=10)
    profile_pic = models.ImageField(upload_to='profile_pics/', default='default_avatar.png')


CATEGORY_CHOICES = [
    ('laptop', 'Laptop'),
    ('prebuilt', 'Prebuilt PC'),
    ('part', 'PC Part'),
]


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"{self.product.name} Image"


class Order(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    billing_address = models.TextField(blank=True, null=True)
    order_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('payment_initiated', 'Payment Initiated'),
            ('processing', 'Processing'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
            ('payment_failed', 'Payment Failed'),
            ('processing_error', 'Processing Error'),
        ],
        default='pending'
    )
    razorpay_order_id = models.CharField(max_length=50, blank=True, null=True)  # Razorpay order ID
    razorpay_payment_id = models.CharField(max_length=50, blank=True, null=True)  # Razorpay payment ID
    razorpay_signature = models.CharField(max_length=100, blank=True, null=True)  # Razorpay signature

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"