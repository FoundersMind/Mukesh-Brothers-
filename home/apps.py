from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'



# def is_quantity_valid(subproduct_instance, selected, requested_quantity):
#     # Calculate the total quantity across all instances in the cart
#     total_quantity_in_cart = CartItem.objects.filter(
#         subproduct=subproduct_instance, unit=selected
#     ).aggregate(models.Sum('quantity'))['quantity__sum'] or 0
