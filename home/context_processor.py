from django.conf import settings

def recent_searches(request):
    recent_searches_product = request.session.get('recent_searches_product', [])
    recent_searches_subproduct = request.session.get('recent_searches_subproduct', [])

    return {
        'recent_searches_product': recent_searches_product,
        'recent_searches_subproduct': recent_searches_subproduct,
    }

def language_switch(request):
    return {
        'LANGUAGES': settings.LANGUAGES,  # Make sure LANGUAGES is defined in settings.py
        'CURRENT_LANGUAGE': request.LANGUAGE_CODE,  # Provides the current language code
    }
