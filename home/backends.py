from django.contrib.auth.backends import BaseBackend
from .models import customer

class MobileNumberBackend(BaseBackend):
    def authenticate(self, request, mobile_number=None):
        try:
            user = customer.objects.get(mobile_number=mobile_number)
            return user
        except customer.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return customer.objects.get(pk=user_id)
        except customer.DoesNotExist:
            return None
