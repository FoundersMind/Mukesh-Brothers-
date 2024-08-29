from django.contrib import admin
from .models import (
    Product, subproduct, inventory, Unit, SpecialProduct, Cart, CartItem, 
    customer, Coupon, Bucket, GSTDiscount, VideoRequest, Order, OrderItem, 
    OwnerDetails, Invoice, Address  # Import the Address model
)

class UnitInline(admin.TabularInline):
    model = Unit
    extra = 0
    fields = ('unit', 'unit_price', 'quantity')
    readonly_fields = ('unit_price', 'quantity')

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
    filter_horizontal = ('coupons',)
    list_filter = ('tag',)
    list_per_page = 20

class SpecialProductAdmin(admin.ModelAdmin):
    inlines = [UnitInline]
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('coupons',)
    list_per_page = 20

class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_amount', 'expiration_date', 'is_active')
    search_fields = ('code',)
    list_filter = ('is_active', 'expiration_date')
    list_per_page = 20

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'tag')
    list_filter = ('tag',)
    search_fields = ('name',)
    list_per_page = 20

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'subproduct', 'special_product', 'quantity', 'unit_price_display', 'is_combo_bundle', 'tag')
    readonly_fields = ('unit_price_display',)
    fields = ('cart', 'unit', 'subproduct', 'quantity', 'unit_price_display', 'special_product', 'is_combo_bundle', 'tag')
    search_fields = ('cart__user__username', 'subproduct__name', 'special_product__name')
    list_filter = ('subproduct', 'special_product', 'is_combo_bundle', 'tag')
    list_per_page = 20

class BucketAdmin(admin.ModelAdmin):
    list_display = ('size', 'discount', 'user')
    list_filter = ('size', 'user')
    list_per_page = 20

class VideoRequestAdmin(admin.ModelAdmin):
    list_display = ('firm_name', 'contact_no', 'submitted_at', 'video')
    fields = ('subproduct', 'firm_name', 'contact_no', 'description', 'user', 'unit', 'video')
    readonly_fields = ('submitted_at',)
    list_per_page = 20

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ('product', 'unit_price', 'quantity', 'total_price')
    readonly_fields = ('total_price',)
    can_delete = True
    show_change_link = True

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('total_price',)
        return ('total_price',)

class InvoiceInline(admin.StackedInline):
    model = Invoice
    extra = 0
    readonly_fields = ('invoice_number', 'issue_date', 'total_amount', 'amount_in_words')

class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'custom_order_id', 'invoice_number', 'location', 'first_name', 'last_name', 'billing_address',
        'firm_name', 'postcode', 'phone', 'email', 'gst_number', 'delivery_address', 'payment_method',
        'total_price', 'bucket_discount', 'coupon_discount', 'final_total_amount', 'status', 'progress_status','created_at', 'order_items_summary'
    )
    list_filter = ('payment_method', 'status', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'status')
    readonly_fields = ('created_at',)
    inlines = [OrderItemInline, InvoiceInline]  # Include order items and invoice inline on the order detail page
    list_per_page = 20  # Pagination for better navigation

    def order_items_summary(self, obj):
        # This method generates a string summary of the order items including units
        items = obj.items.all()  # Fetch related order items
        summary = ', '.join(f"{item.product.name} x {item.quantity} {item.unit}" for item in items)
        return summary

    order_items_summary.short_description = 'Order Items'


@admin.register(OwnerDetails)
class OwnerDetailsAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'ifsc_code', 'upi_id', 'gst_number', 'contact_number')
    search_fields = ('account_number', 'ifsc_code', 'upi_id', 'gst_number')

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'order', 'issue_date', 'total_amount', 'amount_in_words')
    list_filter = ('issue_date',)
    search_fields = ('invoice_number', 'order__custom_order_id')
    readonly_fields = ('issue_date', 'total_amount', 'amount_in_words')
    list_per_page = 20

# Register Address model with admin site
from django.contrib import admin
from .models import Address

class AddressAdmin(admin.ModelAdmin):
    list_display = ('address_type', 'location', 'postcode', 'get_user')  # Display user as well
    search_fields = ('location', 'postcode', 'user__username')  # Allow searching by location, postcode, and user
    list_filter = ('address_type', 'location', 'postcode')  # Filter by address type, location, and postcode
    list_per_page = 20

    def get_user(self, obj):
        return obj.user  # Safely handle cases where the user might be null
    get_user.short_description = 'User'


from django.contrib import admin
from .models import EmailLog

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'subject', 'sent_at', 'status')
    list_filter = ('sent_at', 'status')
    search_fields = ('recipient', 'subject')
    date_hierarchy = 'sent_at'



# Register other models
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
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Address, AddressAdmin)
