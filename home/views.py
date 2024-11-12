# -*- coding: utf-8 -*-
from django.views.decorators.http import require_POST,require_GET
from django.contrib.auth.decorators import login_required
from .models import Product
from django.contrib.auth import logout
# from .models import subproduct
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from .backends import MobileNumberBackend
from twilio.base.exceptions import TwilioRestException
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, Unit, Cart, CartItem, subproduct
from django.http import JsonResponse

# from .models import SpecialSaleProduct
from django.db import models
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from twilio.rest import Client
from django.contrib.auth.models import User
from django.shortcuts import render
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from .models import customer
from decimal import Decimal
from .models import Bucket
from .models import SpecialProduct
from decimal import Decimal
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from django.core.serializers import serialize

from .models import CartItem
# views.py

def logout_view(request):
    logout(request)
    # Redirect to the homepage or login page after logout
    return redirect('home')  # Replace 'home' with the name of your homepage URL or login page URL


from decimal import Decimal, ROUND_DOWN

def index(request):
    products = Product.objects.all()
    special_products = SpecialProduct.objects.prefetch_related('coupons').all()  # Include prefetch_related to fetch coupons
    
    special_data = []
    for special_product in special_products:
        units = Unit.objects.filter(special_product=special_product)
        
        # Calculate the price range for each subproduct
        prices = [unit.unit_price for unit in units if unit.unit_price is not None]
        
        if prices:
            max_price = max(prices).quantize(Decimal('0.01'), rounding=ROUND_DOWN)  # Limit to 2 decimal places
            min_price = (max_price * Decimal('0.95')).quantize(Decimal('0.01'), rounding=ROUND_DOWN)  # Limit to 2 decimal places
        else:
            min_price = max_price = Decimal('0.00')  # Set default to 0.00
        
        special_data.append({
            'special_product': special_product,
            'min_price': min_price,
            'max_price': max_price,
            'units': units,
            'coupons': special_product.coupons.all(),  # Include coupons related to the special product
            'carousel_image_url': special_product.carousel_image.url if special_product.carousel_image else None,
        })
    
    # Fetch all buckets from the database
    buckets = Bucket.objects.all()

    context = {
        'products': products,
        'user': request.user,
        'special_products': special_products,
        'special_data': special_data,
        'buckets': buckets,  # Pass buckets to the template context
    }
    return render(request, 'index.html', context)


    
def login_view(request):
    return render(request,'login.html')

def calculate_unit_price(subproduct_id, united):
    try:
        # Query the database to get the unit price based on subproduct_id and unit
        unit_price = Unit.objects.get(Subproduct_id=subproduct_id, unit=united).unit_price ##((((((important subproduct_id left me capital s rahega warna error occured ka message ayega))))))

        # Make sure that unit_price is a valid number
        return unit_price
    except Unit.DoesNotExist:
        # Handle the case where the specified unit doesn't exist for the subproduct
        return "price not available "
    except Exception as e:
        # Handle any other exceptions or errors that may occur
        return "Error occurred"
def get_unit_price(request):
    subproduct_id = request.GET.get('subproduct_id')  # Updated to match the attribute name used in JavaScript
    united = request.GET.get('unit_received')  # Updated to match the attribute name used in JavaScript

    # Log the values for debugging
    print(f"subproduct_id: {subproduct_id}, united: {united}")

    # Calculate the unit price, ensuring it's a valid numeric value
    unit_price = calculate_unit_price(subproduct_id, united)
    print(unit_price)

    if unit_price is not None:
        # Return the unit price as JSON
        return JsonResponse({'price': unit_price})
    else:
        return JsonResponse({'error': 'Invalid price'}, status=400)
    


def check_quantity(request):
    if request.method == 'GET':
        # Get parameters from the request
        subproduct_id = request.GET.get('subproduct_id')
        requested_quantity = int(request.GET.get('quantity', 1))
        selected_unit = request.GET.get('selectedUnit')  # Get the selected unit from the request

        try:
            # Query the database to get the subproduct
            subproduct_instance = subproduct.objects.get(id=subproduct_id)

            # Get the associated unit for the selectedUnit
            unit = Unit.objects.filter(Subproduct=subproduct_instance, unit=selected_unit).first()

            if unit and unit.quantity is not None and unit.quantity >= requested_quantity:
                # Send JSON response indicating available quantity
                return JsonResponse({'available': True})
            else:
                # If the unit for the selectedUnit is not found or quantity is not sufficient
                return JsonResponse({'available': False, 'message': 'Requested quantity exceeds available quantity limit abcvc'})
        except subproduct.DoesNotExist:
            return JsonResponse({'error': 'Subproduct not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



from django.http import JsonResponse

@require_POST
@login_required
def add_to_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        subproduct_id = request.POST.get('subproduct_id')
        subpr = request.POST.get("subproduct_name")
        united = request.POST.get('unit')
        quantity_str = request.POST.get('quantity')
        tag = request.POST.get('tag')  # Get the tag value from the POST request

        print(f'subproduct_id: {subproduct_id}, subpr: {subpr}, selected: {united}, quantity: {quantity_str}, tag: {tag}')

        if subproduct_id:
            subproduct_instance = get_object_or_404(subproduct, pk=subproduct_id)

            if quantity_str.isdigit():
                quantity = int(quantity_str)
            else:
                return JsonResponse({'error': 'Invalid quantity value'}, status=400)

            unit_price = calculate_unit_price(subproduct_id, united)

            if united not in [choice[0] for choice in Unit.unit_choices]:
                return JsonResponse({'error': 'Invalid unit selection'}, status=400)

            cart, created = Cart.objects.get_or_create(user=request.user)

            existing_cart_item = CartItem.objects.filter(
                Q(cart=cart, subproduct=subproduct_instance, unit__unit=united)
            ).first()

            if existing_cart_item:
                new_total_quantity = existing_cart_item.quantity + quantity

                if new_total_quantity > existing_cart_item.unit.quantity:
                    return JsonResponse({'error': 'Requested quantity exceeds available quantity add to cart'}, status=400)

                existing_cart_item.quantity = new_total_quantity
                existing_cart_item.unit_price = unit_price
                existing_cart_item.save()
            else:
                unit_instance = get_object_or_404(Unit, Subproduct=subproduct_instance, unit=united)
                # Create CartItem with tag value included
                cart_item = CartItem.objects.create(cart=cart, subproduct=subproduct_instance, unit=unit_instance,
                                                    quantity=quantity, tag=tag)

            cart_item_count = CartItem.objects.filter(cart=cart).count()

            return JsonResponse({'success': f"{united} {subproduct_instance.name} added to the cart.", 'cart_item_count': cart_item_count})

from django.http import JsonResponse

@login_required
def add_to_cart_index(request):
    if request.method == 'POST':
        special_product_id = request.POST.get('special_product_id')
        special_product_name = request.POST.get('special_product_name')
        unit = request.POST.get('unit')
        quantity = int(request.POST.get('quantity', 1))
        
        special_product = get_object_or_404(SpecialProduct, id=special_product_id)
        unit_instance = get_object_or_404(Unit, special_product=special_product, unit=unit)
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            special_product=special_product,
            unit=unit_instance
        )

        cart_item.quantity += quantity
        cart_item.save()
        cart_item_count = CartItem.objects.filter(cart=cart).count()
        
        # if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': f"{unit} {special_product.name} added to the cart.", 'cart_item_count': cart_item_count})
       

    return JsonResponse({'error': 'Invalid request'}, status=400)

   

from django.http import JsonResponse

def select_bucket(request):
    if request.method == "POST":
        size = request.POST.get('size')
        discount = request.POST.get('discount')
        
        # Store selected bucket information in session
        request.session['selected_bucket'] = {
            'size': size,
            'discount': discount
        }
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})
from .models import GSTDiscountForm
from .models import GSTDiscount
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import GSTDiscountForm
from .models import GSTDiscount

@login_required
def apply_gst_discount(request):
    if request.method == 'POST' and request.is_ajax():
        form = GSTDiscountForm(request.POST)
        if form.is_valid():
            gst_number = form.cleaned_data['gst_number']
            discount_percentage = form.cleaned_data['discount_percentage']

            # Example logic to apply GST discount
            user = request.user
            gst_discount, created = GSTDiscount.objects.get_or_create(user=user, gst_number=gst_number)
            gst_discount.discount_percentage = discount_percentage
            gst_discount.save()

            # Return JSON response indicating success
            return JsonResponse({'success': True})
        else:
            # Return JSON response with form errors
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        # Invalid request method or not AJAX
        return JsonResponse({'success': False, 'error': 'Invalid request.'})

@login_required
def remove_gst_discount(request):
    if request.method == 'POST' and request.is_ajax():
        try:
            gst_discount = GSTDiscount.objects.get(user=request.user)
            gst_discount.delete()
            return JsonResponse({'success': True})
        except GSTDiscount.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'No GST discount found for the current user.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Failed to remove GST discount: {str(e)}'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request.'})

    
@login_required
def cart_view(request, unit, subproduct_id, unit_price):
    if request.method == 'POST' and request.is_ajax():
        # Extract data from the POST request
        cart_item_id = request.POST.get('cart_item_id')
        new_quantity = int(request.POST.get('quantity'))
        tag = request.POST.get('tag')  # Add this line to get the tag value

        # Update the quantity for the specified cart item
        cart_item = CartItem.objects.get(id=cart_item_id)
        cart_item.quantity = new_quantity
        cart_item.save()

        total_price_item = cart_item.unit.unit_price * new_quantity

        # Recalculate the total cart price
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        total_cart_price = sum(item.unit.unit_price * item.quantity for item in cart_items)

        return JsonResponse({'total_price_item': total_price_item, 'total_cart_price': total_cart_price})
    else:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        total_prices = []
        total_price = 0

        for cart_item in cart_items:
            if cart_item.subproduct:
                cart_item_image = cart_item.subproduct.image.url
            elif cart_item.special_product:
                cart_item_image = cart_item.special_product.image.url
            else:
                cart_item_image = ''

            cart_item.image_url = cart_item_image

            try:
                unit_price = float(cart_item.unit.unit_price)

                total_price_item = unit_price * cart_item.quantity
                total_prices.append(total_price_item)

                # Assign the calculated total_price_item to the cart_item
                cart_item.total_price = total_price_item
                cart_item.save()
            except ValueError:
                print("Invalid value for unit_price")
        if total_prices:
            total_cart_price = sum(total_prices)
        else:
            total_cart_price = 0
        # Calculate or fetch the correct selected bucket for display
        selected_bucket = cart_items.first().selected_bucket if cart_items.exists() else None

        return render(request, 'Cart.html', {'cart_items': cart_items, 'total_price': total_price, 'total_price_all': total_cart_price})
from django.contrib import messages

from django.shortcuts import redirect

from django.http import JsonResponse

# @login_required
# @require_POST
# def create_bundle(request):
#     try:
#         subproduct_id = request.POST.get('subproduct_id')
#         subproduct_name = request.POST.get('subproduct_name')
#         unit = request.POST.get('unit')
#         quantity = int(request.POST.get('quantity', 1))  # Default quantity is 1

#         # Retrieve the subproduct instance
#         subproduct_instance = get_object_or_404(subproduct, pk=subproduct_id)
        
#         # Retrieve the unit instance based on the subproduct and selected unit
#         unit_instance = Unit.objects.filter(Subproduct=subproduct_instance, unit=unit).first()
#         if not unit_instance:
#             raise ValueError("Unit instance not found for subproduct and unit")

#         unit_price = unit_instance.unit_price

#         # Check if the subproduct is valid for bundle creation
#         if subproduct_instance.tag != 'combo_bundle':
#             messages.error(request, 'Selected product is not valid for bundle creation')
#             return JsonResponse({'error': 'Selected product is not valid for bundle creation'}, status=400)

#         # Check if the user has an active cart
#         cart, created = Cart.objects.get_or_create(user=request.user)

#         # Check if an existing bundle is already in the cart
#         bundle = ComboBundle.objects.filter(cart=cart).first()

#         if not bundle:
#             # Create a new bundle if it doesn't exist
#             bundle = ComboBundle.objects.create(
#                 name=subproduct_name + '_Bundle',
#                 discount_percentage=0,
#                 minimum_quantity=10,
#                 minimum_price=unit_price * 10,  # Assuming minimum quantity is 10
#                 cart=cart
#             )

#         # Add the subproduct to the bundle
#         bundle.subproducts.add(subproduct_instance)
#         bundle.save()

#         # Update or create a CartItem for this subproduct in the bundle
#         cart_item, created = CartItem.objects.get_or_create(
#             cart=cart,
#             subproduct=subproduct_instance,
#             unit_price=unit_price,
#             defaults={'quantity': quantity}
#         )
#         if not created:
#             cart_item.quantity += quantity
#             cart_item.save()

#         messages.success(request, 'Subproduct added to bundle successfully')
#         return JsonResponse({'success': 'Subproduct added to bundle successfully'})

#     except Exception as e:
#         messages.error(request, 'An error occurred while adding subproduct to the bundle. Please try again.')
#         print("Error occurred while adding subproduct to bundle:", str(e))
#         return JsonResponse({'error': 'An error occurred while adding subproduct to the bundle. Please try again.'}, status=500)

from decimal import Decimal
from django.http import JsonResponse
from decimal import Decimal
from django.http import JsonResponse
import json


def update_cart_item_quantity(request, cart_item_id):
    # Get the CartItem object
    cart_item = CartItem.objects.get(id=cart_item_id)

    # Get the operation and selected unit from the request
    operation = request.GET.get('operation', 'increment')
    selected_unit = request.GET.get('selectedUnit')
    subproduct_id = request.GET.get('subproduct_id')
    special_product_id=request.GET.get('special_product_id')

    # Update the quantity based on the operation
    if operation == 'decrement':
        cart_item.quantity = max(cart_item.quantity - 1, 1)
    elif operation == 'increment':
        cart_item.quantity += 1

    # Ensure requested quantity is less than or equal to available quantity in the selected unit
    if cart_item.quantity > cart_item.unit.quantity:
        return JsonResponse({'error': 'Requested quantity exceeds available quantity update cart'}, status=400)

    # Update the selected unit for the cart item
    cart_item.selected_unit = selected_unit
    cart_item.save()

    # Calculate the unit price and total price
    unit_price = calculate_unit_price(subproduct_id, selected_unit)
    total_price = unit_price * cart_item.quantity

    # Set a success message
    messages.success(request, f"{cart_item.subproduct.name} quantity updated to {cart_item.quantity}.")
    # messages.success(request, f"{cart_item.special_product.name} quantity updated to {cart_item.quantity}.")
    return JsonResponse({'new_quantity': cart_item.quantity})
def update_cart_item_quantity_index(request, cart_item_id):
    # Get the CartItem object
    cart_item = CartItem.objects.get(id=cart_item_id)

    # Get the operation and selected unit from the request
    operation = request.GET.get('operation', 'increment')
    selected_unit = request.GET.get('selectedUnit')
    subproduct_id = request.GET.get('subproduct_id')
    special_product_id=request.GET.get('special_product_id')

    # Update the quantity based on the operation
    if operation == 'decrement':
        cart_item.quantity = max(cart_item.quantity - 1, 1)
    elif operation == 'increment':
        cart_item.quantity += 1

    # Ensure requested quantity is less than or equal to available quantity in the selected unit
    if cart_item.quantity > cart_item.unit.quantity:
        return JsonResponse({'error': 'Requested quantity exceeds available quantity update cart'}, status=400)

    # Update the selected unit for the cart item
    cart_item.selected_unit = selected_unit
    cart_item.save()

    # Calculate the unit price and total price
    unit_price = calculate_unit_price(subproduct_id, selected_unit)
    total_price = unit_price * cart_item.quantity

    # Set a success message
    messages.success(request, f"{cart_item.special_product.name} quantity updated to {cart_item.quantity}.")
    # messages.success(request, f"{cart_item.special_product.name} quantity updated to {cart_item.quantity}.")
    return JsonResponse({'new_quantity': cart_item.quantity})

# @login_required
def Home(request):
    return render(request,'Home.html') 

def subproduct1(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    subcategories = product.subproduct_set.all()  # Use the reverse relation here

    subproduct_data = []
    for subproduct in subcategories:
        units = subproduct.unit_set.all()

        # Calculate the price range for each subproduct
        prices = [unit.unit_price for unit in units]

        if prices:
            min_price = min(prices)
            max_price = max(prices)
        else:
            min_price = max_price = 0  # Or any other default values you prefer

        subproduct_data.append({
            'subproduct': subproduct,
            'min_price': min_price,
            'max_price': max_price,
            'units': units,
            'image': subproduct.image.url if subproduct.image else None,  # Include the image URL
        })

    return render(request, 'subproduct1.html', {'product': product, 'subproduct_data': subproduct_data})




@require_POST
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    unit_price_integer = int(round(cart_item.unit.unit_price))
    
    # Get the subproduct_id if it exists, else use None
    subproduct_id = cart_item.subproduct.id if cart_item.subproduct else None

    # Get the special_product_id if it exists, else use None
    special_product_id = cart_item.special_product.id if cart_item.special_product else None

    cart_item.delete()

    # Redirect based on which ID is available
    if subproduct_id:
        return redirect('cart_view', unit=cart_item.unit.unit, subproduct_id=subproduct_id, unit_price=unit_price_integer)
    elif special_product_id:
        return redirect('cart_view', unit=cart_item.unit.unit, subproduct_id=0, unit_price=unit_price_integer)
    else:
        return redirect('cart_view', unit=cart_item.unit.unit, subproduct_id=0, unit_price=unit_price_integer)
def send_otp(request):
    if request.method == 'POST':
        # Get the mobile number from the request
        mobile_number = request.POST.get('mobile_number')
        
        # Print the mobile number to the console for debugging
        print(f"Received mobile number: {mobile_number}")

        # Use the Twilio client to send the OTP
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        try:
            verification = client.verify \
                .services(settings.TWILIO_VERIFY_SID) \
                .verifications \
                .create(to=mobile_number, channel="sms")
            print(f"Verification status: {verification.status}")
            return JsonResponse({'success': True, 'message': 'OTP sent successfully'})
        except Exception as e:
            # Print any errors that occur during the Twilio API call
            print(f"Error sending OTP: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Error sending OTP'})

    # Return an error response if the request method is not POST
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

from django.shortcuts import redirect
import uuid

def generate_user_id():
    return str(uuid.uuid4())



def verify_otp(request):
    if request.method == 'POST':
        mobile_number = request.POST.get('mobile_number')
        otp = request.POST.get('otp')
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        try:
            # Verify OTP
            verification_check = client.verify \
                .services(settings.TWILIO_VERIFY_SID) \
                .verification_checks \
                .create(to=mobile_number, code=otp)
            
            if verification_check.status == 'approved':
                # Check if the mobile number exists in the database
                try:
                    customer_instance = customer.objects.get(mobile_number=mobile_number)
                    # Mobile number already registered
                    # Create or get the corresponding Django user
                    user, created = User.objects.get_or_create(username=mobile_number)
                    # Authenticate the user
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    return JsonResponse({'success': True, 'message': 'Mobile number already registered'})
                except customer.DoesNotExist:
                    # Mobile number not registered, create a new user
                    # Generate a unique user ID (you can customize this logic)
                    user_id = generate_user_id()
                    # Create a new user entry
                    new_customer = customer.objects.create(mobile_number=mobile_number)
                    # Create a corresponding Django user
                    user = User.objects.create_user(username=mobile_number, password=None)
                    # Authenticate the user
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    return JsonResponse({'success': True, 'message': 'User registered successfully', 'user_id': user_id})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid OTP'})
            
        except TwilioRestException as e:
            # Handle Twilio API errors
            print(f"Twilio API error: {e}")
            return JsonResponse({'success': False, 'message': 'Error verifying OTP'})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@require_POST
def check_quantity_available(request, subproduct_id):
    subproduct = get_object_or_404(subproduct, id=subproduct_id)
    selected_unit = request.GET.get('unit')
    selected_quantity = int(request.GET.get('quantity', 0))

    # Calculate max_quantity based on related CartItem instances
    max_quantity_in_cart = subproduct.unit_set.aggregate(models.Max('quantity')).get('quantity__max', 0)

    data = {
        'available': selected_quantity <= max_quantity_in_cart
    }

    return JsonResponse(data)


# Assuming you have a function to handle unit selection in your views or wherever you handle user input
def handle_unit_selection(request, cart_item_id, selected_unit):
    cart_item = CartItem.objects.get(pk=cart_item_id)

    # Assuming you have a function to calculate the price based on the selected unit
    selected_unit_price = calculate_unit_price(cart_item.subproduct.id, selected_unit)

    # Update the CartItem fields
    cart_item.selected_unit = selected_unit
    cart_item.selected_unit_price = selected_unit_price

    # Save the changes
    cart_item.save()

from django.shortcuts import redirect
@login_required
def maincart(request):
    # Assuming you have the necessary information to construct the URL
    unit = 'default_unit'  # Replace with the actual default unit
    subproduct_id = 1  # Replace with the actual default subproduct ID
    unit_price = 'default_price'  # Replace with the actual default unit price

    # Redirect to the cart_view with the default parameters
    return redirect('cart_view', unit=unit, subproduct_id=subproduct_id, unit_price=unit_price)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Coupon
from django.utils import timezone
@login_required
def apply_coupon(request):
    if request.method == 'POST':
        # Reset coupon-related session variables if not already set
        if 'coupon_applied' not in request.session:
            request.session['coupon_applied'] = False
            request.session['coupon_code'] = ''
            request.session['coupon_discount'] = 0
            request.session['total_price_after_coupon_discount'] = 0
        
        # Retrieve the coupon code and total cart price from the POST data
        coupon_code = request.POST.get('coupon_code')
        total_cart_price = request.POST.get('total_cart_price')

        # Check if the coupon code exists and is active
        coupon = get_object_or_404(Coupon, code=coupon_code, is_active=True)

        # Check if the coupon has already been applied in this session
        if request.session.get('coupon_applied'):
            return JsonResponse({'success': False, 'message': 'Coupon has already been applied.'})

        # Check if the coupon has expired
        if coupon.expiration_date < timezone.now().date():
            return JsonResponse({'success': False, 'message': 'This coupon has expired.'})

        # Apply the discount from the coupon
        coupon_discount = coupon.discount_amount
        total_price_after_coupon_discount = Decimal(total_cart_price) - coupon_discount

        # Update session to mark coupon as applied and store coupon details
        request.session['coupon_applied'] = True
        request.session['coupon_code'] = coupon_code
        request.session['coupon_discount'] = float(coupon_discount)  # Convert Decimal to float
        request.session['total_price_after_coupon_discount'] = float(total_price_after_coupon_discount)  # Convert Decimal to float

        # Prepare the response data
        response_data = {
            'success': True,
            'coupon_discount': float(coupon_discount),  # Convert Decimal to float
            'total_price_after_coupon_discount': float(total_price_after_coupon_discount)  # Convert Decimal to float
        }

        return JsonResponse(response_data)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request'})
@login_required
def remove_coupon_discount(request):
    if request.method == 'POST':
        # Check if the coupon has been applied
        if not request.session.get('coupon_applied'):
            return JsonResponse({'success': False, 'message': 'No coupon applied.'})

        # Remove coupon discount logic here
        # Reset session variables
        del request.session['coupon_applied']
        del request.session['coupon_code']

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Product, subproduct

def search_results(request):
    query = request.GET.get('q', '')
    search_type = request.GET.get('search_type', 'product')  # Default to 'product' if not specified

    context = {'query': query, 'search_type': search_type}

    if search_type == 'product':
        results = Product.objects.filter(name__icontains=query)
        if results.exists():
            context['products'] = results
            template = 'index.html'
        else:
            # Fetch all products and subproducts for display in no_results.html
            all_products = Product.objects.all()
            all_subproducts = subproduct.objects.all()
            context['all_products'] = all_products
            context['all_subproducts'] = all_subproducts
            template = 'no_results.html'
    elif search_type == 'subproduct':
        subproducts = subproduct.objects.filter(name__icontains=query)
        subproduct_data = []

        for subproduct_item in subproducts:
            units = subproduct_item.unit_set.all()

            # Calculate the price range for each subproduct
            prices = [unit.unit_price for unit in units]

            if prices:
                min_price = min(prices)
                max_price = max(prices)
            else:
                min_price = max_price = 0  # Or any other default values you prefer

            subproduct_data.append({
                'subproduct': subproduct_item,
                'min_price': min_price,
                'max_price': max_price,
                'units': units,
                'image': subproduct_item.image.url if subproduct_item.image else None,  # Include the image URL
            })

        if subproduct_data:
            context['subproduct_data'] = subproduct_data
            context['products_exist'] = True  # Flag to indicate products exist
            template = 'subproduct1.html'
        else:
            # Fetch all products and subproducts for display in no_results.html
            all_products = Product.objects.all()
            all_subproducts = subproduct.objects.all()
            context['all_products'] = all_products
            context['all_subproducts'] = all_subproducts
            context['products_exist'] = False
            template = 'no_results.html'

    else:
        template = 'no_results.html'

    # Update recent searches in session
    if search_type == 'product':
        recent_searches_key = 'recent_searches_product'
    elif search_type == 'subproduct':
        recent_searches_key = 'recent_searches_subproduct'
    else:
        recent_searches_key = None

    if recent_searches_key:
        recent_searches = request.session.get(recent_searches_key, [])
        if query:
            if query not in recent_searches:
                recent_searches.insert(0, query)
                if len(recent_searches) > 5:
                    recent_searches.pop()
                request.session[recent_searches_key] = recent_searches

    # Redirect to index.html with anchor if searching for products
    if search_type == 'product' and template == 'index.html' and '#products-section' not in request.get_full_path():
        return redirect(f"{reverse('home')}#products-section")
    else:
        return render(request, template, context)



import random

def get_products(request):
    products = list(Product.objects.values_list('name', flat=True))
    random_products = random.sample(products, min(len(products), 5))
    return JsonResponse(random_products, safe=False)

def get_subproducts(request):
    subproducts = list(subproduct.objects.values_list('name', flat=True))
    random_subproducts = random.sample(subproducts, min(len(subproducts), 5))
    return JsonResponse(random_subproducts, safe=False)
# def filtered_products(request):
#     tag = request.GET.get('tag')
#     products = Product.objects.all()

#     if tag == 'new':
#         filtered_products = products.filter(tag='new')
#     elif tag == 'best_seller':
#         filtered_products = products.filter(tag='best_seller')
#     else:
#         filtered_products = None  # No tag selected, so show all products

#     # Store filtered products in session
#     request.session['filtered_products'] = list(filtered_products.values_list('id', flat=True)) if filtered_products else []

#     # Redirect to home with anchor if necessary
#     if '#products-section' not in request.get_full_path():
#         return redirect(f"{reverse('home')}#products-section")

#     return render(request, 'index.html', {'products': filtered_products})

def filtered_and_special_data(request):
    # Fetch carousel data (special products)
    special_products = SpecialProduct.objects.prefetch_related('coupons').all()

    special_data = []
    for special_product in special_products:
        units = Unit.objects.filter(special_product=special_product)
        
        # Calculate the price range for each subproduct
        prices = [unit.unit_price for unit in units if unit.unit_price is not None]
        
        if prices:
            max_price = max(prices)
            min_price = max_price * Decimal('0.95')  # Adjust as needed
        else:
            min_price = max_price = 0  # Or set default values
        
        special_data.append({
            'special_product': special_product,
            'min_price': min_price,
            'max_price': max_price,
            'units': units,
            'coupons': special_product.coupons.all(),
            'carousel_image_url': special_product.carousel_image.url if special_product.carousel_image else None,
        })

    # Default to showing all products
    all_products = Product.objects.all()

    # Handle filtering based on tags if provided
    tags = request.GET.getlist('tag')
    if tags:
        filtered_products = all_products.filter(tag__in=tags).distinct()
    else:
        filtered_products = all_products  # No filtering applied

    # Render the template with the appropriate context
    context = {
        'special_data': special_data,
        'products': filtered_products,  # Use filtered_products for the template
    }
    return render(request, 'index.html', context)

from django.shortcuts import redirect, reverse
from .models import subproduct

from django.shortcuts import render, get_object_or_404
from .models import Product, subproduct

from django.shortcuts import get_object_or_404, render


# views.py
from django.shortcuts import render, get_object_or_404


def filtered_subproducts(request, product_id=None):
    # If product_id is provided, fetch the product object or set product to None
    product = get_object_or_404(Product, pk=product_id) if product_id else None

    # Fetch all subproducts related to the given product or all subproducts if no product_id
    subproducts = product.subproduct_set.all() if product else subproduct.objects.all()

    # Get filter parameters from the request
    subproduct_id = request.GET.get('subproduct')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    tags = request.GET.getlist('tags')  # Get list of tags

    # Prepare subproduct data with min and max prices
    subproduct_data = []
    for subproduct in subproducts:
        units = subproduct.unit_set.all()
        prices = [unit.unit_price for unit in units]

        if prices:
            min_price = min(prices)
            max_price = max(prices)
        else:
            min_price = max_price = 0

        subproduct_data.append({
            'subproduct': subproduct,
            'min_price': min_price,
            'max_price': max_price,
            'units': units,
            'image': subproduct.image.url if subproduct.image else None,
        })

    # Filter subproduct_data based on user input
    if price_min:
        subproduct_data = [data for data in subproduct_data if data['min_price'] >= float(price_min)]

    if price_max:
        subproduct_data = [data for data in subproduct_data if data['max_price'] <= float(price_max)]

    # Filter by subproduct_id
    if subproduct_id:
        subproduct_data = [data for data in subproduct_data if data['subproduct'].id == int(subproduct_id)]

    # Filter by tags
    if tags:
        filtered_subproduct_data = []
        for data in subproduct_data:
            if any(tag in data['subproduct'].tag for tag in tags):
                filtered_subproduct_data.append(data)
        subproduct_data = filtered_subproduct_data

    # Context for template rendering
    context = {
        'product': product,
        'subproduct_data': subproduct_data,
    }

    return render(request, 'subproduct1.html', context)
def filtered_subproducts_without_product(request):
    # Fetch all subproducts when no product_id is provided
    subproducts = subproduct.objects.all()

    # Get filter parameters from the request
    subproduct_id = request.GET.get('subproduct')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    tags = request.GET.getlist('tags')  # Get list of tags

    # Prepare subproduct data with min and max prices
    subproduct_data = []
    for subproduct_obj in subproducts:
        units = subproduct_obj.unit_set.all()
        prices = [unit.unit_price for unit in units]

        if prices:
            min_price = min(prices)
            max_price = max(prices)
        else:
            min_price = max_price = 0

        subproduct_data.append({
            'subproduct': subproduct_obj,
            'min_price': min_price,
            'max_price': max_price,
            'units': units,
            'image': subproduct_obj.image.url if subproduct_obj.image else None,
        })

    # Filter subproduct_data based on user input
    if price_min:
        subproduct_data = [data for data in subproduct_data if data['min_price'] >= float(price_min)]

    if price_max:
        subproduct_data = [data for data in subproduct_data if data['max_price'] <= float(price_max)]

    # Filter by subproduct_id
    if subproduct_id:
        subproduct_data = [data for data in subproduct_data if data['subproduct'].id == int(subproduct_id)]

    # Filter by tags
    if tags:
        filtered_subproduct_data = []
        for data in subproduct_data:
            if any(tag in data['subproduct'].tag for tag in tags):
                filtered_subproduct_data.append(data)
        subproduct_data = filtered_subproduct_data

    # Context for template rendering
    context = {
        'subproduct_data': subproduct_data,
    }

    return render(request, 'subproduct1.html', context)


from django.shortcuts import redirect
from django.utils.translation import activate
from django.shortcuts import redirect
from django.conf import settings
from django.shortcuts import redirect
from django.utils.translation import activate
from django.conf import settings
def set_language(request):
    if request.method == 'POST' and 'language' in request.POST:
        language_code = request.POST['language']
        
        # Optional: Validate language_code here if needed
        
        try:
            activate(language_code)
            request.session[settings.LANGUAGE_SESSION_KEY] = language_code
            return JsonResponse({'status': 'success'})  # Optional: Return JSON response indicating success
        except LookupError:
            # Handle invalid language_code gracefully
            return JsonResponse({'status': 'error', 'message': 'Invalid language code'})  # Optional: Return JSON response with error message
    
    # Handle if language code is not provided in POST data
    return JsonResponse({'status': 'error', 'message': 'Language code not provided'})  # Optional: Return JSON response with error message

from django.template.loader import render_to_string


from .models import CartItem  # Import your CartItem model

from django.http import JsonResponse

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from .models import CartItem

@login_required
@require_POST
def checkout_view(request):
    # Retrieve discounted total amount from POST data
    discounted_total_amount = request.POST.get('discounted_total_amount')
    bucket_discount = request.POST.get('bucket_discount')

    # Example: Check if any discount message was sent from JavaScript
    discount_message = request.POST.get('discount_message', None)
    
    # Determine which discounts were applied
    applied_discounts = []
    if request.POST.get('gst_discount_applied'):
        applied_discounts.append('GST Discount')
    if request.POST.get('coupon_discount_applied'):
        applied_discounts.append('Coupon Discount')
    if request.POST.get('combo_discount_applied'):
        applied_discounts.append('Combo Discount')
    
    # Retrieve cart items for the current user
    cart_items = CartItem.objects.filter(cart__user=request.user, quantity__gt=0)
    total_items = cart_items.count()
    total_cart_price = sum(item.unit_price * item.quantity for item in cart_items)
    
    # Simulate shipping address and payment method (replace with actual logic)
    shipping_address = "123 Shipping Street, City, Country"
    payment_method = "Credit Card"
    
    # Render order confirmation template with context
    context = {
        'cart_items': cart_items,
        'total_items': total_items,
        'total_cart_price': total_cart_price,
        'shipping_address': shipping_address,
        'payment_method': payment_method,
        'bucket_discount': bucket_discount,
        'discounted_total_amount': discounted_total_amount,
        'applied_discounts': applied_discounts,
        'discount_message': discount_message,
    }
    
    return render(request, 'order_confirmation.html', context)

from django.http import JsonResponse
from .models import CartItem
from django.http import JsonResponse


import json

@csrf_exempt  # Ensure CSRF protection is handled appropriately
def clear_cart(request):
    if request.method == 'POST':
        try:
            # Assume you have a way to get the current user's cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart.items.all().delete()  # Remove all items from the cart
            return JsonResponse({'success': True})
        except Exception as e:
            print(f'Error clearing cart: {e}')
            return JsonResponse({'success': False, 'error': 'Failed to clear cart.'}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)
    
@require_POST
@login_required
def add_to_bucket(request):
    try:
        data = json.loads(request.body)
        selectedItems = data.get('selectedItems', [])

        totalWeight = 0
        for item in selectedItems:
            totalWeight += calculate_weight(item['unit'], item['quantity'])

        bucketSize = request.session.get('selected_bucket', {}).get('size', '5kg')  # Default size if not set

        # Determine discount based on total weight and bucket size
        discountPercent = None
        message = ''

        if bucketSize == '5kg':
            if totalWeight >= 1 and totalWeight <= 5:
                discountPercent=2
                message="will be available after in checkout"
            elif totalWeight>10:
                message = 'Please choose Bucket size of  20kg  to avail the discount.'
            else:
                message = 'Please choose Bucket size of  10kg or more to avail the discount.'
        elif bucketSize == '10kg':
            if totalWeight > 5 and totalWeight <= 10:
                discountPercent = 8
                message="will be available after in checkout"
            elif totalWeight > 10:
                message = 'Please increase the Bucket size  to avail the discount.'

            else:
                message = 'Please Add more then 5kg to avail the discount.'
        elif bucketSize == '20kg':
            if totalWeight > 10 and totalWeight < 20:
                discountPercent = 12
                message="will be available after in checkout"
            else:
                message = 'Please Add more than 10kg to avail the discount.'
        else:
            message = 'Invalid bucket size selected.'
            discountPercent=0

        # Add items to bucket or perform any necessary actions here

        # Return JSON response with total weight, discount, and message
        return JsonResponse({
            'message': message,
            'total_weight': totalWeight,
            'discount_percent': discountPercent
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format in request body.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def calculate_weight(unit, quantity):
    if 'kg' in unit.lower():
        return float(unit.lower().replace('kg', '').strip()) * quantity
    elif 'gm' in unit.lower() or 'g' in unit.lower():
        return float(unit.lower().replace('gm', '').replace('g', '').strip()) * quantity / 1000
    else:
        return 0.0  # Default case if unit format is not recognized

def get_bucket_limit(size):
    try:
        bucket_size = float(''.join(filter(str.isdigit, size)))
        if 'kg' in size.lower():
            return bucket_size  # Return bucket size in kg
        else:
            return bucket_size * 1000  # Convert kg to grams if size is in grams
    except ValueError:
        return 0.0  # Default case if size is not recognized
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from .models import Order, OrderItem
from django.contrib.auth.models import User
import requests
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Order, OrderItem, subproduct
from num2words import num2words  # Import the num2words library
from .models import Order, OrderItem, subproduct,EmailLog
@csrf_exempt
@login_required
def submit_order(request):
    if request.method == 'POST':
        # Extract form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        billing_address = request.POST.get('billing_address')
        location = request.POST.get('location')
        firm_name = request.POST.get('firm_name', '')
        postcode = request.POST.get('postcode')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        gst_number = request.POST.get('gst_number', '')
        delivery_address = request.POST.get('delivery_address', '')
        payment_method = request.POST.get('payment_method')
        cash_payment_type = request.POST.get('cash_option', '')  # Updated field for Cash on Delivery options
        total_items = int(request.POST.get('total_items', 0))  # Extract total_items as an integer

        # Safely extract and convert decimal values
        def get_decimal_value(key, default='0.00'):
            try:
                return Decimal(request.POST.get(key, default))
            except (ValueError, InvalidOperation):
                return Decimal(default)

        # Extract discounts and final total amount from the request
        try:
            total_price = get_decimal_value('total_price')
            bucket_discount = get_decimal_value('bucket_discount')
            coupon_discount = get_decimal_value('coupon_discount')
            final_total_amount = get_decimal_value('total_discounted_price')
        except (ValueError, InvalidOperation) as e:
            return JsonResponse({'error': str(e)}, status=400)

        # Convert final_total_amount to words
        try:
            final_total_amount_in_words = num2words(final_total_amount, lang='en')
        except Exception as e:
            return JsonResponse({'error': f'Error converting amount to words: {str(e)}'}, status=500)

        # Handle order items
        try:
            order_items_data = json.loads(request.POST.get('order_items_data', '[]'))
            if not order_items_data:
                return JsonResponse({'error': 'No order items provided'}, status=400)
            
            order_items = []
            for item in order_items_data:
                subproduct_name = item.get('subproduct_name')
                unit = item.get('unit')
                image_url = item.get('image_url')
                subproduct_instance = subproduct.objects.filter(name=subproduct_name).first()

                if subproduct_instance:
                    order_items.append({
                        'subproduct_name': subproduct_instance.name,
                        'unit': unit,
                        'unit_price': Decimal(item.get('unit_price', '0.00')),
                        'quantity': int(item.get('quantity', 0)),
                        'item_total': Decimal(item.get('item_total', '0.00')),
                        'image_url': image_url,
                    })
                else:
                    return JsonResponse({'error': f'Subproduct with name {subproduct_name} does not exist'}, status=400)
        except (ValueError, json.JSONDecodeError) as e:
            return JsonResponse({'error': str(e)}, status=400)

        # Check if the user is authenticated
        user = request.user if request.user.is_authenticated else None

        # Generate custom_order_id
        current_date = datetime.now().strftime("%Y%m%d")
        random_number = get_random_string(length=4, allowed_chars='0123456789')
        payment_prefix = {
            'cash': 'C',
            'online': 'O'
        }.get(payment_method, 'X')

        if payment_method == 'cash' and cash_payment_type:
            cash_prefix = {'normal': 'N', 'credit': 'C'}.get(cash_payment_type, 'X')
            custom_order_id = f"{payment_prefix}{cash_prefix}{current_date}{random_number}"
        else:
            custom_order_id = f"{payment_prefix}{current_date}{random_number}"

        # Create the order first
        order = Order(
            user=user,
            first_name=first_name,
            last_name=last_name,
            billing_address=billing_address,
            location=location,
            firm_name=firm_name,
            postcode=postcode,
            phone=phone,
            email=email,
            gst_number=gst_number,
            delivery_address=delivery_address,
            payment_method=payment_method,
            cash_payment_type=cash_payment_type,
            total_items=total_items,  # Include total_items in the order
            total_price=total_price,
            bucket_discount=bucket_discount,
            coupon_discount=coupon_discount,
            final_total_amount=final_total_amount,
            amount_in_words=final_total_amount_in_words,
            status='pending',
            custom_order_id=custom_order_id
        )
        order.save()

        # Create and save invoice after creating the order
        invoice_number = f'INV-{custom_order_id}'
        invoice = Invoice.objects.create(
            invoice_number=invoice_number,
            order=order,
            issue_date=datetime.now(),
            total_amount=final_total_amount,
            amount_in_words=final_total_amount_in_words
        )

        # Update the order with the invoice number
        order.invoice_number = invoice_number
        order.save()

        # Save order items
        for item in order_items:
            OrderItem.objects.create(
                order=order,
                product=subproduct.objects.get(name=item['subproduct_name']),
                unit=item['unit'],
                unit_price=item['unit_price'],
                quantity=item['quantity'],
                total_price=item['item_total'],
                image=item['image_url']
            )

        # Generate QR code for the invoice
        invoice_url = request.build_absolute_uri(f'/download_invoice/{custom_order_id}/')
        qr_code_data = generate_qr_code(invoice_url)
        qr_code_image = ContentFile(qr_code_data, f'{custom_order_id}.png')
        invoice.qr_code.save(f'{custom_order_id}.png', qr_code_image, save=True)

        # Clear cart or perform other actions after saving the order
        request.session['cart_items'] = []  # Clear cart items from session

        # Set a session variable to indicate order confirmation
        request.session['order_confirmed'] = True

        # Return the custom_order_id in the JSON response
        return JsonResponse({'order_id': custom_order_id, 'cash_payment_type': cash_payment_type})

    return JsonResponse({'error': 'Invalid request method'}, status=405)

from django.shortcuts import render, redirect
from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponseBadRequest

@login_required
def order_confirmed(request, order_id):
    try:
        # Check if the session is already locked
        if request.session.get('checkout_locked'):
            return JsonResponse({'error': 'Checkout is locked. Please wait until the process is complete.'}, status=403)
        
        # Lock the session to prevent duplicate order processing
        request.session['checkout_locked'] = True

        # Retrieve and confirm the order
        order = get_object_or_404(Order, custom_order_id=order_id)
        
        # Clear the cart items
        cart = request.user.cart
        cart.items.clear()  # This will clear the ManyToMany relationship

        # Reset coupon-related session variables
        request.session['coupon_applied'] = False
        request.session['coupon_code'] = ''
        request.session['coupon_discount'] = 0
        request.session['total_price_after_coupon_discount'] = 0

        # Clear the session lock after processing
        del request.session['checkout_locked']

        # Redirect to the new view that will render the order_confirmed.html
        return redirect('order_confirmed_view', order_id=order_id)
    
    except Cart.DoesNotExist:
        # Clear the session lock if an error occurs
        request.session.pop('checkout_locked', None)
        return JsonResponse({'error': 'Cart does not exist for this user'}, status=400)
    except Exception as e:
        # Clear the session lock if an error occurs
        request.session.pop('checkout_locked', None)
        return JsonResponse({'error': str(e)}, status=500)

from django.shortcuts import render, get_object_or_404

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
@csrf_exempt
@login_required
def clear_order_confirmed_flag(request):
    if request.method == 'POST':
        # Clear the session flag
        request.session.pop('order_confirmed_displayed', None)
        return JsonResponse({'status': 'flag cleared'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from django.templatetags.static import static
from django.core.mail import EmailMessage
from django.utils.timezone import now
def contact_us(request):
    return render(request, 'contact_us.html')
@login_required
def order_confirmed_view(request, order_id):
    # Check if the session flag is set
    if request.session.get('order_confirmed_displayed'):
        return redirect('/')

    # Retrieve the order to be displayed
    order = get_object_or_404(Order, custom_order_id=order_id)

    # Generate the static URL for the logo
    logo_url = static('logo.png')

    # Prepare email content
    subject = 'Order Confirmation'
    html_message = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                border: 1px solid #ddd;
                padding: 20px;
            }}
            .header {{
                text-align: center;
                padding: 10px;
                background-color: #f4f4f4;
            }}
            .header img {{
                max-width: 200px;
                height: auto;
            }}
            .content {{
                padding: 20px;
            }}
            .content h2 {{
                color: #333;
            }}
            .content p {{
                color: #666;
            }}
            .footer {{
                text-align: center;
                padding: 10px;
                background-color: #f4f4f4;
                font-size: 12px;
                color: #666;
            }}
            .footer a {{
                color: #1a73e8;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="https://www.flipkart.com/pixaplay-54-projector-aug24-store" alt="Company Logo">
            </div>
            <div class="content">
                <h2>Order Confirmation</h2>
                <p>Dear {order.first_name} {order.last_name},</p>
                <p>Your order with ID {order_id} has been confirmed.</p>
                <p><strong>Order Details:</strong></p>
                <ul>
                    <li>Total Price: {order.total_price}</li>
                    <li>Bucket Discount: {order.bucket_discount}</li>
                    <li>Coupon Discount: {order.coupon_discount}</li>
                    <li>Final Total Amount: {order.final_total_amount}</li>
                </ul>
                <p>Thank you for your purchase!</p>
                <p>Best regards,</p>
                <p>Mukesh & Brothers</p>
            </div>
            <div class="footer">
                <p>&copy; {now().year} Mukesh & Brothers. All rights reserved.</p>
                <p><a href="https://example.com/unsubscribe">Unsubscribe</a></p>
            </div>
        </div>
    </body>
    </html>
    '''
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [order.email]

    try:
        email = EmailMessage(
            subject,
            html_message,
            from_email,
            recipient_list
        )
        email.content_subtype = 'html'  # Important for HTML emails
        email.send()
        status = 'Sent'
    except Exception as e:
        status = f'Failed: {str(e)}'

    # Log email details
    EmailLog.objects.create(
        recipient=order.email,
        subject=subject,
        status=status
    )

    # Set the session flag to prevent refreshing or going back
    request.session['order_confirmed_displayed'] = True

    # Render the order_confirmed.html template with the order details
    return render(request, 'order_confirmed.html', {'order': order})






from django.shortcuts import render
from .models import Order

from datetime import datetime, timedelta

from datetime import datetime, timedelta
from django.shortcuts import render
from .models import Order  # Ensure this imports your Order model
@login_required
def my_orders(request):
    user = request.user if request.user.is_authenticated else None

    # Get filter parameters from the request
    status_filter = request.GET.get('status', '')  # Order status filter
    date_filter = request.GET.get('date', '')      # Date filter (e.g., '30_days', '2023', '2024')
    sort_filter = request.GET.get('sort', 'latest') # Sort filter (e.g., 'latest', 'oldest')
    
    if user:
        orders = Order.objects.filter(user=user)
        
        # Apply status filter
        if status_filter:
            orders = orders.filter(progress_status=status_filter)
        
        # Apply date filter
        if date_filter == '30_days':
            thirty_days_ago = datetime.now() - timedelta(days=30)
            orders = orders.filter(created_at__gte=thirty_days_ago)
        elif date_filter.isdigit():  # Assume it's a year filter
            orders = orders.filter(created_at__year=date_filter)
        
        # Apply sort filter
        if sort_filter == 'latest':
            orders = orders.order_by('-created_at')  # Newest first
        elif sort_filter == 'oldest':
            orders = orders.order_by('created_at')   # Oldest first
    else:
        orders = []

    return render(request, 'my_order.html', {
        'orders': orders,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'sort_filter': sort_filter,
    })


@csrf_exempt
def create_cashfree_session(request, order_id):
    if request.method == 'POST':
        try:
            order = Order.objects.get(custom_order_id=order_id)
            customer_id = str(request.user.id)  # Use the logged-in user's ID

            headers = {
                'Content-Type': 'application/json',
                'x-api-version': '2022-01-01',
                'x-client-id': settings.CASHFREE_APP_ID,
                'x-client-secret': settings.CASHFREE_SECRET_KEY,
                'Accept': 'application/json',
            }

            data = {
                'order_id': order_id,
                'order_amount': str(order.final_total_amount),
                'order_currency': 'INR',
                'customer_details': {
                    'customer_id': customer_id,
                    'customer_name': f"{order.first_name} {order.last_name}",
                    'customer_email': order.email,
                    'customer_phone': order.phone,
                },
                'order_note': 'Order note if any',
            }

            response = requests.post(
                'https://sandbox.cashfree.com/pg/orders',  # Use production URL if not in sandbox mode
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                response_data = response.json()
                payment_url = response_data.get('payment_link')  # Ensure this key matches the response from Cashfree
                if payment_url:
                    return JsonResponse({'payment_url': payment_url})  # Return the payment URL
                else:
                    return JsonResponse({'error': 'Payment URL not found in response'}, status=500)
            else:
                return JsonResponse({
                    'error': 'Failed to create Cashfree order',
                    'details': response.json()
                }, status=400)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def cashfree_callback(request):
    if request.method == 'POST':
        try:
            # Extract response data
            response_data = json.loads(request.body.decode('utf-8'))

            # Verify response data and status
            order_id = response_data.get('order_id')
            order_status = response_data.get('order_status')

            # Check the order status
            if order_status == 'SUCCESS':
                # Update the order status in the database
                order = Order.objects.get(custom_order_id=order_id)
                order.status = 'completed'  # Update to completed or similar status
                order.save()

                # Redirect to home page or thank-you page
                return redirect('home')  # Adjust the URL name as needed

            return JsonResponse({'error': 'Payment failed'}, status=400)

        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


from django.shortcuts import render

import pdfkit
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, OwnerDetails  # Assuming OrderItem is the model for order items



def invoice_html(request, order_id):
    # Fetch order and related items
    order = get_object_or_404(Order, custom_order_id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    # Generate QR code for invoice download
    invoice_url = request.build_absolute_uri(f'/download_invoice/{order_id}/')
    qr_code_data = generate_qr_code(invoice_url)
    qr_code_image = ContentFile(qr_code_data, f'{order_id}.png')

    # Save QR code image if not already saved
    if not order.qr_code:
        order.qr_code.save(f'{order_id}.png', qr_code_image, save=True)

    # Fetch owner details
    owner_details = OwnerDetails.objects.first()

    if not owner_details:
        owner_account_details = {
            'account_number': 'N/A',
            'ifsc_code': 'N/A',
            'upi_id': 'N/A',
            'gst_number': 'N/A',
            'address': 'N/A',
            'contact_number': 'N/A',
        }
    else:
        owner_account_details = {
            'account_number': owner_details.account_number,
            'ifsc_code': owner_details.ifsc_code,
            'upi_id': owner_details.upi_id,
            'gst_number': owner_details.gst_number,
            'address': owner_details.address,
            'contact_number': owner_details.contact_number,
        }

    # Generate HTML for the invoice
    html_string = render_to_string('invoice.html', {
        'order': order,
        'order_items': order_items,
        'owner_account_details': owner_account_details,
        'qr_code_url': order.qr_code.url if order.qr_code else None,
    })

    response = HttpResponse(html_string, content_type='text/html')
    return response

from django.shortcuts import render, get_object_or_404
from .models import Order, OrderItem,OwnerDetails
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from django.http import HttpResponse

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=2,  # Reduced size
        border=2,    # Reduced border size
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

from django.shortcuts import get_object_or_404, render
from django.core.files.base import ContentFile
from .models import Order, OrderItem, Invoice, OwnerDetails

import re
import re  # Ensure regex is imported
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile

from decimal import Decimal, ROUND_DOWN
import re
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from .models import Order, OrderItem, Invoice, OwnerDetails


@login_required
def view_invoice(request, custom_order_id):
    # Fetch the order and its associated items
    order = get_object_or_404(Order, custom_order_id=custom_order_id)
    order_items = OrderItem.objects.filter(order=order)

    total_unit_quantity = 0  # Initialize total unit quantity

    for item in order_items:
        print(f"Processing item with unit: {item.unit}")
        
        # Match unit value and type, allowing for optional spaces
        match = re.match(r"(\d+)\s*(Grams|Kilogram)", item.unit.strip())
        
        if match:
            unit_value = int(match.group(1))
            unit_type = match.group(2)
            print(f"Match found: {match.groups()}")

            # Convert to kilograms
            unit_in_kg = unit_value / 1000 if unit_type == "Grams" else unit_value
            item.unit_quantity = unit_in_kg * item.quantity
            total_unit_quantity += item.unit_quantity
        else:
            print(f"No match for unit: {item.unit}")

        # Get GST rate from the corresponding subproduct
        subproduct = item.product  # Get the associated subproduct
        print(subproduct)
        
        # Ensure subproduct has a valid gst_rate before proceeding
        if hasattr(subproduct, 'gst_rate'):
            gst_rate = Decimal(subproduct.gst_rate)/100  # Convert GST rate from percentage to decimal
            item.gst_rate = subproduct.gst_rate
            print(gst_rate)

            # Calculate Price Before GST using the total price
            item.price_before_gst = item.total_price / (1 + gst_rate)
            item.price_before_gst = item.price_before_gst.quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            print(item.price_before_gst)

            # Calculate the GST Amount based on the price before GST
            item.gst_amount = item.price_before_gst * gst_rate
            item.gst_amount = item.gst_amount.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

            # Save the updated item
            item.save()
        else:
            print(f"Subproduct {subproduct} does not have a gst_rate.")

    # Update order with the total unit quantity
    order.total_unit_quantity = total_unit_quantity
    order.save()

    # Generate QR code for invoice download
    invoice_url = request.build_absolute_uri(f'/download_invoice/{custom_order_id}/')
    qr_code_data = generate_qr_code(invoice_url)
    qr_code_image = ContentFile(qr_code_data, f'{custom_order_id}.png')

    invoice, created = Invoice.objects.get_or_create(
        order=order,
        defaults={
            'invoice_number': f'INV-{custom_order_id}',
            'issue_date': order.created_at,
            'total_amount': order.final_total_amount,
            'amount_in_words': order.amount_in_words  
        }
    )

    if not invoice.qr_code:
        invoice.qr_code.save(f'{custom_order_id}.png', qr_code_image, save=True)
        invoice.save()

    owner_details = OwnerDetails.objects.first()

    if not owner_details:
        owner_account_details = {
            'account_number': 'N/A',
            'ifsc_code': 'N/A',
            'upi_id': 'N/A',
            'gst_number': 'N/A',
            'address': 'N/A',
            'contact_number': 'N/A',
        }
    else:
        owner_account_details = {
            'account_number': owner_details.account_number,
            'ifsc_code': owner_details.ifsc_code,
            'upi_id': owner_details.upi_id,
            'gst_number': owner_details.gst_number,
            'address': owner_details.address,
            'contact_number': owner_details.contact_number,
        }

    context = {
        'order': order,
        'order_items': order_items,
        'owner_account_details': owner_account_details,
        'qr_code_url': invoice.qr_code.url if invoice.qr_code else None,
        'total_unit_quantity': total_unit_quantity,
    }

    return render(request, 'invoice.html', context)





from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import VideoRequest
from .forms import VideoRequestForm
@require_POST
@login_required
def submit_video_request(request):
    form = VideoRequestForm(request.POST)
    if form.is_valid():
        video_request = form.save(commit=False)
        video_request.user = request.user
        video_request.save()
        return JsonResponse({'success': True, 'message': 'Your request has been submitted successfully. We wil contact you within 2 days'})
    else:
        # For debugging purposes, you might want to log the errors
        import json
        errors = form.errors.get_json_data()
        print("Form errors:", json.dumps(errors, indent=2))  # Log errors to the server console
        return JsonResponse({'success': False, 'errors': errors}, status=400)
    
from django.shortcuts import render
from django.contrib.auth.decorators import login_required



from django.shortcuts import render, redirect, get_object_or_404
from .models import Order
from django.contrib.auth.decorators import login_required
# views.py

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Address
from .forms import AddressForm
import json
from django.shortcuts import render
from .models import Address

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, Address
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Address
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Address, Order
from django.shortcuts import render
from .models import Coupon
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

@csrf_exempt
def save_address(request):
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        address_type = request.POST.get('address_type')
        address_details = request.POST.get('address_details')
        location = request.POST.get('location')
        postcode = request.POST.get('postcode')
        
        if address_id:  # If address_id is present, update existing address
            try:
                address = Address.objects.get(id=address_id)
                address.address_type = address_type
                address.address_details = address_details
                address.location = location
                address.postcode = postcode
                address.save()
                success = True
                message = 'Address updated successfully'
            except Address.DoesNotExist:
                success = False
                message = 'Address not found'
        else:  # If address_id is not present, create a new address
            address = Address(
                address_type=address_type,
                address_details=address_details,
                location=location,
                postcode=postcode,
                user=request.user  # Assuming the Address model has a user field
            )
            address.save()
            success = True
            message = 'Address saved successfully'
        
        return JsonResponse({
            'success': success,
            'message': message
        })
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def delete_address(request, address_id):
    if request.method == 'DELETE':
        address = get_object_or_404(Address, id=address_id)
        address.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def account(request):
    # Fetch the pending order for the logged-in user
    order = Order.objects.filter(user=request.user, status='pending').first()
    coupons = Coupon.objects.filter(is_active=True)  # Only active coupons
   
    # Fetch all addresses for the logged-in user
    saved_addresses = request.user.addresses.all()
    
    # Combine data into the context
    context = {
        'order': order,
        'saved_addresses': saved_addresses,
        'coupons':coupons
    }
    
    return render(request, 'account.html', context)


# views.py

# views.py

from django.shortcuts import get_object_or_404, redirect
from .models import Order
from .notification import notify_order_status_change

def update_order_status(request, custom_order_id):
    order = get_object_or_404(Order, custom_order_id=custom_order_id)
    new_status = request.POST.get('status')
    order.progress_status = new_status
    order.save()
    
    # Notify clients about the status change
    notify_order_status_change(order)
    
    return redirect('order_detail', custom_order_id=order.custom_order_id)


from django.http import JsonResponse
from google.cloud import translate_v2 as translate
import os

def translate_text(request):
    if request.method == "GET":
        text = request.GET.get('text')
        target_language = request.GET.get('target_language')

        if text and target_language:
            translate_client = translate.Client()

            # Perform the translation
            result = translate_client.translate(text, target_language=target_language)

            # Return the translated text
            return JsonResponse({'translated_text': result['translatedText']})
        else:
            return JsonResponse({'error': 'Invalid parameters'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Product, subproduct
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

# # Function to generate QR code for Product and Subproduct
# def generate_qr_code(request, model_name, pk):
#     # Determine if it's Product or Subproduct
#     if model_name == 'product':
#         obj = get_object_or_404(Product, pk=pk)
#     elif model_name == 'subproduct':
#         obj = get_object_or_404(subproduct, pk=pk)
#     else:
#         return HttpResponse("Invalid model name", status=400)

#     # Generate QR code pointing to the product's or subproduct's admin page
#     product_url = f"{request.build_absolute_uri('/')}/admin/home/{model_name}/{obj.id}/change/"
#     qr = qrcode.make(product_url)

#     # Save the QR code image
#     qr_image = BytesIO()
#     qr.save(qr_image, format="PNG")
#     qr_image.seek(0)
    
#     # Save it to the corresponding model
#     if model_name == 'product':
#         obj.qr_code.save(f"product_{obj.id}_qr.png", ContentFile(qr_image.read()), save=True)
#     elif model_name == 'subproduct':
#         obj.qr_code.save(f"subproduct_{obj.id}_qr.png", ContentFile(qr_image.read()), save=True)

#     return HttpResponse("QR code generated successfully!")

# Function to handle QR code scanning for Product and Subproduct
def scan_qr_code(request):
    # Implement logic for scanning QR code (you can use a library or frontend JS for scanning)
    scanned_data = request.POST.get('scanned_data')  # This should come from the frontend scanner
    
    # Check whether the scanned data matches a Product or Subproduct
    try:
        # Assuming the scanned data is the model's primary key (ID)
        product = Product.objects.get(pk=scanned_data)
        return redirect(f"/admin/home/product/{product.id}/change/")
    except Product.DoesNotExist:
        try:
            sub_product = subproduct.objects.get(pk=scanned_data)
            return redirect(f"/admin/home/subproduct/{sub_product.id}/change/")
        except subproduct.DoesNotExist:
            return HttpResponse("QR code does not match any Product or Subproduct.", status=404)




def chatbot_view(request):
    return render(request, 'chatbot.html')


