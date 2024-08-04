from django import forms
from .models import VideoRequest

class VideoRequestForm(forms.ModelForm):
    class Meta:
        model = VideoRequest
        fields = ['firm_name', 'contact_no', 'description', 'subproduct', 'unit']

from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'billing_address', 'city_town', 'firm_name', 'postcode', 'phone', 'email', 'gst_number', 'delivery_address', 'payment_method']
