from django.core.management.base import BaseCommand
from home.models import Product  # Assuming your product model is here
from django.core.cache import cache
import json

# Define product categories for each season
SEASONAL_CATEGORIES = {
    "summer": ["Oil", "Cold Drinks", "Dry Fruits"],
    "winter": ["Spices", "Ghee", "Honey"],
    "rainy": ["Tea", "Snacks", "Pickles"]
}

class Command(BaseCommand):
    help = "Precompute and store seasonal product recommendations in Redis"

    def handle(self, *args, **kwargs):
        seasonal_products = {}

        for season, categories in SEASONAL_CATEGORIES.items():
            seasonal_products[season] = list(
                Product.objects.filter(category__name__in=categories).values("id", "name", "image")
            )

        cache.set("seasonal_products", json.dumps(seasonal_products), timeout=None)
        self.stdout.write(self.style.SUCCESS("✅ Seasonal products stored in Redis"))
