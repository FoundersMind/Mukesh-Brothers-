from django.contrib import admin
from .models import (
    Product, subproduct, inventory, Unit, SpecialProduct, Cart, CartItem, 
    customer, Coupon, Bucket, GSTDiscount, VideoRequest, Order, OrderItem
)

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

class VideoRequestAdmin(admin.ModelAdmin):
    list_display = ('firm_name', 'contact_no', 'submitted_at', 'video')
    fields = ('subproduct', 'firm_name', 'contact_no', 'description', 'user', 'unit', 'video')
    readonly_fields = ('submitted_at',)

    def get_subproduct_name(self, obj):
        return obj.subproduct.name if obj.subproduct else 'No Subproduct'
    get_subproduct_name.short_description = 'Subproduct Name'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Number of empty forms to display
    fields = ('product', 'unit_price', 'quantity', 'total_price')
    readonly_fields = ('total_price',)  # Make 'total_price' read-only
    can_delete = True  # Allow deleting items from inline
    show_change_link = True  # Show link to change item if necessary

    def get_readonly_fields(self, request, obj=None):
        # Make 'unit_price' and 'total_price' read-only if editing existing Order
        if obj:
            return ('total_price',)  # Adjust based on your needs
        return ('total_price',)  # Adjust based on your needs

class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'first_name', 'last_name', 'billing_address', 
        'city_town', 'firm_name', 'postcode', 'phone', 'email', 
        'gst_number', 'delivery_address', 'payment_method', 
        'total_price', 'bucket_discount', 'coupon_discount', 
        'final_total_amount', 'status', 'created_at', 'order_items_summary'
    )
    list_filter = ('payment_method', 'status')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'status')
    readonly_fields = ('created_at',)

    def order_items_summary(self, obj):
        # This method generates a string summary of the order items
        items = obj.items.all()  # Fetch related order items
        summary = ', '.join(f"{item.product.name} x {item.quantity}" for item in items)
        return summary

    order_items_summary.short_description = 'Order Items'  # Display name in list view

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
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
admin.site.register(VideoRequest, VideoRequestAdmin)
