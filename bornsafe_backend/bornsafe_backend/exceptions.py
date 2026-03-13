from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('bornsafe')

def custom_exception_handler(exc, context):
    """Gestionnaire d'exceptions personnalisé"""
    
    # Appeler le gestionnaire par défaut
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data['status_code'] = response.status_code
        
        # Logguer l'erreur
        logger.error(
            f"Exception: {exc.__class__.__name__} - "
            f"Detail: {str(exc)} - "
            f"User: {context['request'].user if context['request'].user.is_authenticated else 'Anonymous'}"
        )
    else:
        # Erreurs non gérées par DRF
        logger.exception(f"Unhandled exception: {str(exc)}")
        response = Response(
            {
                'error': 'Une erreur inattendue est survenue',
                'detail': str(exc) if context['request'].user.is_superuser else None
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response
