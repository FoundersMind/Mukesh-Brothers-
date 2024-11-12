from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect

from .models import (
    Product, subproduct, inventory, Unit, SpecialProduct, Cart, CartItem, 
    customer, Coupon, Bucket, GSTDiscount, VideoRequest, Order, OrderItem, 
    OwnerDetails, Invoice, Address, EmailLog  # Import necessary models
)
import qrcode
from django.core.files.base import ContentFile
from io import BytesIO

def generate_qr_code(obj):
    # Generate a string to encode in the QR code (you can customize this)
    qr_data = f"{obj.pk}"  # Using the primary key for unique identification
    img = qrcode.make(qr_data)  # Create QR code image

    # Save the image to a BytesIO object
    buffer = BytesIO()
    img.save(buffer, format='PNG')  # Save as PNG
    buffer.seek(0)

    # Create a ContentFile to save in the ImageField
    return ContentFile(buffer.read(), name=f"{obj.name}_qr.png")  # Generate a unique filename

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
    list_display = ('name', 'tag', 'product', 'qr_code')
    search_fields = ('name', 'product__name')
    filter_horizontal = ('coupons',)
    list_filter = ('tag',)
    list_per_page = 20

    readonly_fields = ('qr_code',)

    def save_model(self, request, obj, form, change):
        if not change and not obj.qr_code:  # Generate QR code only for new objects
            obj.qr_code = generate_qr_code(obj)
        super().save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate_qr/<int:subproduct_id>/', self.admin_site.admin_view(self.generate_qr), name='generate_qr_subproduct'),
            path('scan_qr/<int:subproduct_id>/', self.admin_site.admin_view(self.scan_qr), name='scan_qr_subproduct'),
        ]
        return custom_urls + urls

    def generate_qr(self, request, subproduct_id):
        subproduct = self.get_object(request, subproduct_id)
        if subproduct and not subproduct.qr_code:  # Generate QR code if it doesn't exist
            subproduct.qr_code = generate_qr_code(subproduct)
            subproduct.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def scan_qr(self, request, subproduct_id):
        # Logic for scanning QR code (this could be a separate view if needed)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'tag', 'qr_code')  # Display QR code
    list_filter = ('tag',)
    search_fields = ('name', 'qr_code')  # Search by QR code
    list_per_page = 20

    readonly_fields = ('qr_code',)

    def save_model(self, request, obj, form, change):
        if not change and not obj.qr_code:  # Generate QR code only for new objects
            obj.qr_code = generate_qr_code(obj)
        super().save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate_qr/<int:product_id>/', self.admin_site.admin_view(self.generate_qr), name='generate_qr'),
            path('scan_qr/<int:product_id>/', self.admin_site.admin_view(self.scan_qr), name='scan_qr'),
        ]
        return custom_urls + urls

    def generate_qr(self, request, product_id):
        product = self.get_object(request, product_id)
        if product and not product.qr_code:  # Generate QR code if it doesn't exist
            product.qr_code = generate_qr_code(product)
            product.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def scan_qr(self, request, product_id):
        # Logic for scanning QR code (this could be a separate view if needed)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# Remaining admin classes (e.g., SpecialProductAdmin, CouponAdmin, etc.)

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
    readonly_fields = ('product', 'unit_price', 'quantity','unit_quantity' ,'total_price')
   
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

from django.contrib import admin

class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'custom_order_id', 'invoice_number', 'location', 'first_name', 'last_name', 'billing_address',
        'firm_name', 'postcode', 'phone', 'email', 'gst_number', 'delivery_address', 'payment_method',
        'total_price', 'bucket_discount', 'coupon_discount', 'final_total_amount', 'display_total_unit_quantity',  # Updated field
        'status', 'progress_status', 'created_at', 'order_items_summary'
    )
    list_filter = ('payment_method', 'status', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'status')
    readonly_fields = ('created_at',)
    inlines = [OrderItemInline, InvoiceInline]  # Include order items and invoice inline on the order detail page
    list_per_page = 20  # Pagination for better navigation

    def display_total_unit_quantity(self, obj):
        # Return total unit quantity in kilograms and append "kg"
        return f"{obj.total_unit_quantity} kg"

    display_total_unit_quantity.short_description = 'Total Unit Quantity (kg)'  # Label for admin list

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
    list_filter = ('sent_at','status')
    search_fields = ('recipient', 'subject')
    readonly_fields = ('sent_at',)
    list_per_page = 20

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

