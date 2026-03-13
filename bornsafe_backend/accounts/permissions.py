from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """
    Permission pour les super admins uniquement
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'super_admin'
        )

class IsMairieOrSuperAdmin(permissions.BasePermission):
    """
    Permission pour les mairies et super admins
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['mairie', 'super_admin']
        )

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission pour permettre à un utilisateur de modifier uniquement ses objets
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user or request.user.role == 'super_admin'
