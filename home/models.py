# -*- coding: utf-8 -*-

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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







