# -*- coding: utf-8 -*-

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
from django.views.decorators.http import require_POST
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



def index(request):
    products = Product.objects.all()
    special_products = SpecialProduct.objects.prefetch_related('coupons').all()  # Include prefetch_related to fetch coupons
    
    special_data = []
    for special_product in special_products:
        units = Unit.objects.filter(special_product=special_product)
        
        # Calculate the price range for each subproduct
        prices = [unit.unit_price for unit in units if unit.unit_price is not None]
        
        if prices:
            max_price = max(prices)
            min_price = max_price * Decimal('0.95')  # Convert the float value to a Decimal object
        else:
            min_price = max_price = 0  # Or any other default values you prefer
        
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
    return render(request,'Login.html')

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


@login_required
@require_POST
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

def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        total_cart_price = request.POST.get('total_cart_price')

        # Check if the coupon code exists
        coupon = get_object_or_404(Coupon, code=coupon_code, is_active=True)

        # Check if the coupon has already been applied
        if request.session.get('coupon_applied'):
            return JsonResponse({'success': False, 'message': 'Coupon has already been applied.'})

        # Apply the discount from the coupon
        coupon_discount = coupon.discount_amount
        total_price_after_coupon_discount = Decimal(total_cart_price) - coupon_discount

        # Update session to mark coupon as applied
        request.session['coupon_applied'] = True
        request.session['coupon_code'] = coupon_code
        request.session['coupon_discount'] = float(coupon_discount)  # Convert Decimal to float
        request.session['total_price_after_coupon_discount'] = float(total_price_after_coupon_discount)  # Convert Decimal to float

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

@login_required
@require_POST
def checkout_view(request):
    # Retrieve discounted total amount from POST data
    discounted_total_amount = request.POST.get('discounted_total_amount')
    bucket_discount = request.POST.get('bucket_discount')

    # Example: Check if any discount message was sent from JavaScript
    discount_message = request.POST.get('discount_message', None)
    
    # Example: Determine which discounts were applied
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
    total_price = sum(item.unit_price * item.quantity for item in cart_items)
    
    # Simulate shipping address and payment method (replace with actual logic)
    shipping_address = "123 Shipping Street, City, Country"
    payment_method = "Credit Card"
    
    context = {
        'cart_items': cart_items,
        'total_items': total_items,
        'total_price': total_price,
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
from django.views.decorators.http import require_POST
import json
@require_POST
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
            elif totalWeight>10:
                message = 'Please choose Bucket size of  20kg  to avail the discount.'
            else:
                message = 'Please choose Bucket size of  10kg or more to avail the discount.'
        elif bucketSize == '10kg':
            if totalWeight > 5 and totalWeight <= 10:
                discountPercent = 8
            elif totalWeight > 10:
                message = 'Please increase the Bucket size  to avail the discount.'

            else:
                message = 'Please choose more then 5kg to avail the discount.'
        elif bucketSize == '20kg':
            if totalWeight > 10 and totalWeight < 20:
                discountPercent = 12
            else:
                message = 'Please choose more than 10kg to avail the discount.'
        else:
            message = 'Invalid bucket size selected.'

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
from django.http import HttpResponse,HttpResponseNotAllowed

@require_POST
def submit_order(request):
    # Process the submitted form data to finalize the order
    if request.method == 'POST':
        # Example: Save order details and calculate total amount
        # Replace this with your actual order processing logic

        # Create the invoice content (example function)
        invoice_content = generate_invoice_content(request.POST)  # Example function to generate invoice content
        
        # Save the invoice content to a file or database (adjust as per your storage method)

        # Return rendered invoice content for download
        response = HttpResponse(invoice_content, content_type='application/pdf')  # Adjust content type as needed
        response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'  # Force download as PDF
        return response

    # If it's not a POST request, return a Method Not Allowed response
    return HttpResponseNotAllowed(['POST'])


def generate_invoice_content(post_data):
    # Example function to generate invoice content (HTML or PDF)
    # Replace with your logic to generate invoice content based on form data
    first_name = post_data.get('first_name', '')
    last_name = post_data.get('last_name', '')
    billing_address = post_data.get('billing_address', '')
    city_town = post_data.get('city_town', '')
    firm_name = post_data.get('firm_name', '')
    postcode = post_data.get('postcode', '')
    phone = post_data.get('phone', '')
    email = post_data.get('email', '')
    gst_number = post_data.get('gst_number', '')
    delivery_address = post_data.get('delivery_address', '')

    # Calculate total amount and other details based on form data
    total_amount = 0  # Replace with your logic to calculate total amount
    
    # Render the invoice template with form data
    invoice_content = render_to_string('invoice.html', {
        'first_name': first_name,
        'last_name': last_name,
        'billing_address': billing_address,
        'city_town': city_town,
        'firm_name': firm_name,
        'postcode': postcode,
        'phone': phone,
        'email': email,
        'gst_number': gst_number,
        'delivery_address': delivery_address,
        'total_amount': total_amount,
    })

    return invoice_content