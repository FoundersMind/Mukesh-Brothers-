# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import Product, subproduct, inventory, Unit, SpecialProduct, Cart, CartItem, customer, Coupon, Bucket,GSTDiscount

class UnitInline(admin.TabularInline):
    model = Unit
    extra = 0
    fields = ('unit', 'unit_price', 'quantity')

class SubproductAdmin(admin.ModelAdmin):
    TAG_CHOICES = [
        ('new', 'New'),
        ('best_seller', 'Best Seller'),
        ('combo_bundle', 'Combo/Bundle'),
        # Add more tag options here as needed
    ]

    inlines = [UnitInline]
    list_display = ('name', 'tag', 'product')
    search_fields = ('name', 'product__name')
    filter_horizontal = ('coupons',)  # Ensure you have 'coupons' defined in subproduct model
    list_filter = ('tag',)
    search_fields = ('name',)

class SpecialProductAdmin(admin.ModelAdmin):
    inlines = [UnitInline]
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('coupons',)  # Ensure you have 'coupons' defined in SpecialProduct model

class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_amount', 'expiration_date', 'is_active')
    search_fields = ('code',)
    list_filter = ('is_active', 'expiration_date')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'tag')
    list_filter = ('tag',)
    search_fields = ('name',)

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'subproduct', 'special_product', 'quantity', 'unit_price_display', 'is_combo_bundle', 'tag')
    readonly_fields = ('unit_price_display',)
    fields = ('cart', 'unit', 'subproduct', 'quantity', 'unit_price_display', 'special_product', 'is_combo_bundle', 'tag')
    search_fields = ('cart__user__username', 'subproduct__name', 'special_product__name')
    list_filter = ('subproduct', 'special_product', 'is_combo_bundle', 'tag')

class BucketAdmin(admin.ModelAdmin):
    list_display = ('size', 'discount', 'user')
    list_filter = ('size', 'user')

admin.site.register(inventory)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(subproduct, SubproductAdmin)
admin.site.register(SpecialProduct, SpecialProductAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Unit)
admin.site.register(customer)
admin.site.register(Bucket, BucketAdmin)

admin.site.register(GSTDiscount)