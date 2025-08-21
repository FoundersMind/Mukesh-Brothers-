from .models import subproduct

def fetch_subproducts():
    """Fetch all subproduct names from the database."""
    return list(subproduct.objects.values_list('name', flat=True))

# Example usage:
subproducts = fetch_subproducts()
print(subproducts)  # Prints the list of all subproduct names
