from django import forms
from .models import VideoRequest

class VideoRequestForm(forms.ModelForm):
    class Meta:
        model = VideoRequest
        fields = ['firm_name', 'contact_no', 'description', 'subproduct', 'unit']

from django import forms
from .models import Order,Address
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'billing_address', 'location',  # Replace city_town with location
            'firm_name', 'postcode', 'phone', 'email', 'gst_number',
            'delivery_address', 'payment_method'
        ]
# forms.py
from django import forms
from .models import Address

class AddressForm(forms.ModelForm):
    LOCATION_CHOICES = [
        ('Shivpuri', 'Shivpuri'),
        ('Indore', 'Indore'),
    ]

    location = forms.ChoiceField(choices=LOCATION_CHOICES, widget=forms.RadioSelect)
    
    class Meta:
        model = Address
        fields = ['address_type', 'address_details', 'location', 'postcode']

    def clean_postcode(self):
        postcode = self.cleaned_data.get('postcode')
        if not postcode.isdigit() or len(postcode) != 6:
            raise forms.ValidationError('Postcode must be a 6-digit number.')
        return postcode
