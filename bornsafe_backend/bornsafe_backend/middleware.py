import logging
import time
from django.utils import timezone

logger = logging.getLogger('bornsafe')

class RequestLoggingMiddleware:
    """Middleware pour logger toutes les requêtes"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Temps de début
        start_time = time.time()
        
        # Traitement de la requête
        response = self.get_response(request)
        
        # Temps de fin
        duration = time.time() - start_time
        
        # Logger la requête
        logger.info(
            f"Request: {request.method} {request.path} - "
            f"User: {request.user if request.user.is_authenticated else 'Anonymous'} - "
            f"Status: {response.status_code} - Duration: {duration:.2f}s"
        )
        
        return response
