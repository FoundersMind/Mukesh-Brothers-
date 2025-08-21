from django import forms
from django.utils.translation import gettext_lazy as _
from .models import VideoRequest, Order, Address

# Form for VideoRequest model
class VideoRequestForm(forms.ModelForm):
    class Meta:
        model = VideoRequest
        fields = ['firm_name', 'contact_no', 'description', 'subproduct', 'unit']
        labels = {
            'firm_name': _('Firm Name'),
            'contact_no': _('Contact Number'),
            'description': _('Description'),
            'subproduct': _('Subproduct'),
            'unit': _('Unit'),
        }

# Form for Order model
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'billing_address', 'location',  # Replace city_town with location
            'firm_name', 'postcode', 'phone', 'email', 'gst_number',
            'delivery_address', 'payment_method'
        ]
        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'billing_address': _('Billing Address'),
            'location': _('Location'),
            'firm_name': _('Firm Name'),
            'postcode': _('Postcode'),
            'phone': _('Phone'),
            'email': _('Email'),
            'gst_number': _('GST Number'),
            'delivery_address': _('Delivery Address'),
            'payment_method': _('Payment Method'),
        }

# Form for Address model
class AddressForm(forms.ModelForm):
    LOCATION_CHOICES = [
        ('Shivpuri', _('Shivpuri')),
        ('Indore', _('Indore')),
    ]

    location = forms.ChoiceField(choices=LOCATION_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = Address
        fields = ['address_type', 'address_details', 'location', 'postcode']
        labels = {
            'address_type': _('Address Type'),
            'address_details': _('Address Details'),
            'location': _('Location'),
            'postcode': _('Postcode'),
        }

    def clean_postcode(self):
        postcode = self.cleaned_data.get('postcode')
        if not postcode.isdigit() or len(postcode) != 6:
            raise forms.ValidationError(_('Postcode must be a 6-digit number.'))
        return postcode
