# -*- coding: utf-8 -*-
from django.utils import timezone
import random
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.db import models
from django import forms
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth.models import User
import uuid

class Product(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='product_images', null=True, blank=True)
    tag = models.CharField(
        max_length=20,
        choices=[
            ('', 'None'),
            ('new', 'New'),
            ('best_seller', 'Best Seller')
        ],
        blank=True,
        default=''
    )

    def __str__(self):
        return self.name

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    expiration_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
    


class SpecialProduct(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='product_images', null=True, blank=True)
    carousel_image = models.ImageField(upload_to='carousel_images', null=True, blank=True)
    coupons = models.ManyToManyField(Coupon, blank=True)
    
    def __str__(self):
        return self.name
    
class subproduct(models.Model):
    TAG_CHOICES = [
        ('', 'None'),
        ('new', 'New'),
        ('best_seller', 'Best Seller'),
        ('combo', 'Combo')  # Added combo/bundle option
    ]
    
    name = models.CharField(max_length=200)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='product_images', null=True, blank=True)
    coupons = models.ManyToManyField(Coupon, blank=True)
    tag = models.CharField(
        max_length=20,
        choices=TAG_CHOICES,
        blank=True,
        default=''
    )
    bucket = models.ForeignKey('Bucket', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.name

class Unit(models.Model):
    Subproduct = models.ForeignKey(subproduct, on_delete=models.CASCADE, null=True, blank=True)

    special_product = models.ForeignKey(SpecialProduct, on_delete=models.CASCADE, null=True, blank=True)
    
    unit_choices = (
        ('10gm', '10 Grams'),
        ('50gm', '50 Grams'),
        ('100gm', '100 Grams'),
        ('250gm', '250 Grams'),
        ('500gm', '500 Grams'),
        ('1kg', '1 Kilogram'),
        ('10kg', '10 Kilogram'),
        ('50kg', '50 Kilogram'),
        ('100kg', '100 Kilogram'),
    )
    
    unit_price = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # Allow null for default calculation
    unit = models.CharField(max_length=20, choices=unit_choices)
    quantity = models.PositiveIntegerField(default=0, null=True)

    def selected_unit(self):
        for choice in self.unit_choices:
            if choice[0] == self.unit:
                return choice[1]
        return ''  # Default value if the unit is not found in choices

    def __str__(self):
        return self.get_unit_display()
    
class UnitInline(admin.TabularInline):
    model = Unit
    extra = 0
    fields = ('unit', 'unit_price', 'quantity')

class SubproductAdmin(admin.ModelAdmin):
    inlines = [UnitInline]

class SpecialProductAdmin(admin.ModelAdmin):
    inlines = [UnitInline]

class inventory(models.Model):
    CATEGORY_CHOICES = [
        ('Category 1', 'Category 1'),
        ('Category 2', 'Category 2'),
        ('Category 3', 'Category 3'),
    ]

    product_name = models.CharField(max_length=100, null=False, blank=False)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    cost = models.DecimalField(max_digits=20, decimal_places=3, null=False, blank=False)
    quantity_available = models.DecimalField(max_digits=10, decimal_places=3, null=False, blank=False)
    unit_choices = (
        ('grams', 'Grams'),
        ('kg', 'Kilograms'),
    )

    unit = models.CharField(max_length=20, choices=unit_choices, default='grams')
    image = models.ImageField(upload_to='media/', null=True, blank=True)
    stock_date = models.DateField(auto_now_add=True)
    last_sales_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.product_name


class Bucket(models.Model):
    size_choices = (
        ('5kg', '5kg'),
        ('10kg', '10kg'),
        ('20kg', '20kg'),
    )

    size = models.CharField(max_length=20, choices=size_choices)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='bucket_images/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.get_size_display()} - {self.user.username}"

from django import forms


class GSTDiscount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gst_number = models.CharField(max_length=15, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"User: {self.user.username} - GST Number: {self.gst_number} - Discount: {self.discount_percentage}%"
    
# forms.py


class GSTDiscountForm(forms.ModelForm):
    class Meta:
        model = GSTDiscount
        fields = ['gst_number', 'discount_percentage']

class Cart(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    items = models.ManyToManyField(Unit, through='CartItem')

    def get_total_weight(self):
        total_weight = 0
        for item in self.cartitem_set.all():
            unit_weight = self.convert_to_kg(item.unit.unit, item.unit.quantity)
            total_weight += unit_weight
        return total_weight

    def get_discount(self):
        total_weight = self.get_total_weight()
        if total_weight <= 5:
            return 0.02
        elif total_weight <= 10:
            return 0.08
        elif total_weight <= 20:
            return 0.12
        return 0

    def convert_to_kg(self, unit, quantity):
        conversion = {
            '10gm': 0.01,
            '50gm': 0.05,
            '100gm': 0.1,
            '250gm': 0.25,
            '500gm': 0.5,
            '1kg': 1,
            '10kg': 10,
            '50kg': 50,
            '100kg': 100,
        }
        return conversion.get(unit, 0) * quantity

    def get_discounted_total(self):
        total_price = sum(item.total_price for item in self.cartitem_set.all())
        discount = self.get_discount()
        return total_price * (1 - discount)

    def get_gst_discounts(self):
        return GSTDiscount.objects.filter(user=self.user)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    subproduct = models.ForeignKey(subproduct, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    special_product = models.ForeignKey(SpecialProduct, on_delete=models.CASCADE, null=True, blank=True)
    is_combo_bundle = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    TAG_CHOICES = [
        ('', 'None'),
        ('new', 'New'),
        ('best_seller', 'Best Seller'),
        ('combo', 'Combo')
    ]
    
    tag = models.CharField(
        max_length=20,
        choices=TAG_CHOICES,
        blank=True,
        default=''
    )
    selected_bucket = models.ForeignKey(Bucket, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.unit:
            self.unit_price = self.unit.unit_price
        super().save(*args, **kwargs)

    def get_unit_price(self):
        return self.unit.unit_price if self.unit else None

    def __str__(self):
        return f'CartItem {self.id} for Cart {self.cart.id}'

    def unit_price_display(self):
        return self.unit.unit_price if self.unit else None
    unit_price_display.short_description = 'Unit Price'


class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['subproduct', 'quantity', 'unit', 'unit_price']



class customer(models.Model):
    mobile_number = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.mobile_number

@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)

# forms.py

# models.py
from django.db import models
from django.contrib.auth.models import User

class VideoRequest(models.Model):
    subproduct = models.ForeignKey(subproduct, on_delete=models.CASCADE, null=True, blank=True)
    firm_name = models.CharField(max_length=255)
    contact_no = models.CharField(max_length=15)
    description = models.TextField()
    submitted_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # New field
    unit = models.CharField(max_length=50, blank=True, null=True)  # New field
    video = models.FileField(upload_to='videos/', null=True, blank=True)  # New field for video upload

    def __str__(self):
        subproduct_name = self.subproduct.name if self.subproduct else 'No Subproduct'
        return f"{self.firm_name} - {subproduct_name} - {self.submitted_at}"


from django.db import models
from django.contrib.auth.models import User
import random
from datetime import datetime
from num2words import num2words
class Invoice(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='invoice_related')
    invoice_number = models.CharField(max_length=20, unique=True, blank=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_in_words = models.CharField(max_length=255, blank=True)
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)  # Optional QR code for invoice
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            current_date = datetime.now()
            date_str = current_date.strftime("%Y%m%d")
            random_number = random.randint(1000, 9999)
            self.invoice_number = f"INV{date_str}{random_number}"

        if not self.amount_in_words:
            self.amount_in_words = num2words(self.total_amount, to='currency', lang='en')
        
        super(Invoice, self).save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.invoice_number} for Order {self.order.custom_order_id}"

class Order(models.Model):
    PROGRESS_STATUS_CHOICES = [
        ('placed', 'Placed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),  # Added cancelled status
    ]
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('online', 'Online'),
    ]

    CASH_PAYMENT_CHOICES = [
        ('normal', 'Normal'),
        ('credit', 'Credit'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    billing_address = models.TextField()
    location = models.CharField(max_length=100)  # Added location field
    firm_name = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    gst_number = models.CharField(max_length=50, blank=True)
    delivery_address = models.TextField(blank=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    cash_payment_type = models.CharField(max_length=10, choices=CASH_PAYMENT_CHOICES, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    bucket_discount = models.DecimalField(max_digits=10, decimal_places=2)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    progress_status = models.CharField(max_length=20, choices=PROGRESS_STATUS_CHOICES, default='placed')
    created_at = models.DateTimeField(auto_now_add=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    custom_order_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    amount_in_words = models.CharField(max_length=255, blank=True)  # New field for amount in words
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE, null=True, blank=True, related_name='order_related')
    total_items = models.PositiveIntegerField(default=0)
    placed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Generate a custom order ID if not already set
        if not self.custom_order_id:
            current_date = datetime.now()
            date_str = current_date.strftime("%Y%m%d")
            random_number = random.randint(100, 999)
            payment_prefix = {
                'cash': 'C',
                'online': 'O'
            }.get(self.payment_method, 'X')
            
            if self.payment_method == 'cash' and self.cash_payment_type:
                payment_prefix += {'normal': 'N', 'credit': 'C'}.get(self.cash_payment_type, 'X')
            
            self.custom_order_id = f"{payment_prefix}{date_str}{random_number}"
        
        # Update the amount in words before saving
        if not self.amount_in_words:
            self.amount_in_words = self.convert_amount_to_words(self.final_total_amount)

        # Update status timing fields
        if self.progress_status == 'placed' and not self.placed_at:
            self.placed_at = timezone.now()
        elif self.progress_status == 'shipped' and not self.shipped_at:
            self.shipped_at = timezone.now()
        elif self.progress_status == 'delivered' and not self.delivered_at:
            self.delivered_at = timezone.now()
        elif self.progress_status == 'cancelled' and not self.cancelled_at:
            self.cancelled_at = timezone.now()

        super(Order, self).save(*args, **kwargs)

    def convert_amount_to_words(self, amount):
        # Function to convert amount to words
        pass

    def __str__(self):
        return f"Order {self.custom_order_id} by {self.first_name} {self.last_name}"

from django.db import models

class EmailLog(models.Model):
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100)  # e.g., 'Sent', 'Failed'

    def __str__(self):
        return f'{self.subject} to {self.recipient}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(subproduct, on_delete=models.CASCADE)  # Assuming you have a Product model
    unit = models.CharField(max_length=50, blank=True, null=True)  # Add a field for unit
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.URLField(max_length=200, blank=True, null=True)  # Add field for image URL

    def __str__(self):
        return f"Item {self.product.name} for Order {self.order.id}"
    
from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator

class OwnerDetails(models.Model):
    account_number = models.CharField(
        max_length=20,
        validators=[MinLengthValidator(9)],
        help_text="Enter the bank account number."
    )
    ifsc_code = models.CharField(
        max_length=11,
        validators=[RegexValidator(r'^[A-Z]{4}0[A-Z0-9]{6}$')],
        help_text="Enter the IFSC code (e.g., KKBR2345677)."
    )
    upi_id = models.CharField(
        max_length=50,
        validators=[RegexValidator(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+$')],
        help_text="Enter the UPI ID (e.g., 8770500434@ybl)."
    )
    gst_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^[A-Z0-9]{15}$')],
        help_text="Enter the GST number."
    )
    address = models.TextField(
        help_text="Enter the owner's address."
    )
    contact_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\d{10,15}$')],
        help_text="Enter the contact number."
    )

    def __str__(self):
        return f"Owner Details ({self.account_number})"

    class Meta:
        verbose_name = "Owner Detail"
        verbose_name_plural = "Owner Details"



# your_app/models.py
from django.db import models
from django.contrib.auth.models import User  # Replace with your custom user model if needed
# models.py

from django.db import models
from django.contrib.auth.models import User  # Import the User model

class Address(models.Model):
    LOCATION_CHOICES = [
        ('Shivpuri', 'Shivpuri'),
        ('Indore', 'Indore'),
    ]

    ADDRESS_TYPE_CHOICES = [
        ('billing', 'Billing Address'),
        ('delivery', 'Delivery Address'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', null=True, blank=True)  # Link to the User model
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES)
    address_details = models.TextField(default='No address details provided')
    location = models.CharField(max_length=255, choices=LOCATION_CHOICES)  # Use choices here
    postcode = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.address_type} - {self.location} ({self.user})"



