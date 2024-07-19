# -*- coding: utf-8 -*-

from django.contrib import admin
from django.urls import path
from home import views
from django.conf import settings
from django.conf.urls.static import static
# from .views import add_to_cart, cart_view
from django.contrib.auth import views as auth_views
from django.urls import path, register_converter
from . import views
from .converters import FloatConverter

# Register the custom converter
register_converter(FloatConverter, 'float')
urlpatterns = [
    path('', views.index, name='home'),
   
    path('filtered_and_special_data/', views.filtered_and_special_data, name='filtered_and_special_data'),
    path('filtered-subproducts/', views.filtered_subproducts_without_product, name='filtered_subproducts_without_product'),
    path('filtered-subproducts/<int:product_id>/', views.filtered_subproducts, name='filtered_subproducts'),
    path('checkout_view/', views.checkout_view, name='checkout_view'),
    path('submit_order/', views.submit_order, name='submit_order'),
    path('Login/', views.login_view, name='Login'),
   
    path('subproduct/<int:product_id>/', views.subproduct1, name='subproduct1'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('add_to_cart_index/', views.add_to_cart_index, name='add_to_cart_index'),
    path('add_to_bucket/', views.add_to_bucket, name='add_to_bucket'),
    path('select-bucket/', views.select_bucket, name='select_bucket'),
    path('Cart/<str:unit>/<int:subproduct_id>/<str:unit_price>/', views.cart_view, name='cart_view'),
    path('main_cart/',views.maincart,name='main_cart'),
    path('get_unit_price/', views.get_unit_price, name='get_unit_price'),
    path('Cart/', views.cart_view, name='cart_view_general'),
    path('logout/', views.logout_view, name='logout'),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart_item_quantity/<int:cart_item_id>/', views.update_cart_item_quantity, name='update_cart_item_quantity'),
    path('update_cart_item_quantity_index/<int:cart_item_id>/', views.update_cart_item_quantity_index, name='update_cart_item_quantity_index'),
    path('check_quantity_available/<int:subproduct_id>/', views.check_quantity_available, name='check_quantity_available'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('check_quantity/', views.check_quantity, name='check_quantity'),
    path('cart_view/', views.cart_view, name='cart_view'),  # Update this line
    path('apply-gst-discount/', views.apply_gst_discount, name='apply_gst_discount'),
    path('remove-gst-discount/', views.remove_gst_discount, name='remove_gst_discount'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove_coupon_discount/', views.remove_coupon_discount, name='remove_coupon_discount'),
    path('search/', views.search_results, name='search_results'),
    path('get_products/', views.get_products, name='get_products'),
    path('get_subproducts/', views.get_subproducts, name='get_subproducts'),

]

    


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

##setting.debug because in setting.py i have set setting.debug=True(it shows that error would be showing in enabled mode if any)