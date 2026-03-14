import logging

logger = logging.getLogger('bornsafe')

class SessionDebugMiddleware:
    """Middleware pour debugger les sessions"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Avant la vue
        if request.user.is_authenticated:
            logger.info(f"Session avant: user={request.user.username}, session_key={request.session.session_key}")
        
        response = self.get_response(request)
        
        # Après la vue
        if request.user.is_authenticated:
            logger.info(f"Session après: user={request.user.username}, session_key={request.session.session_key}")
        
        return response
