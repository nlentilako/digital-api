from rest_framework import permissions
from apps.users.models import User


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit items.
    Read-only access is allowed for all other users.
    """
    
    def has_permission(self, request, view):
        # Allow read-only access for any request
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write permissions only for admin users
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admin users.
    """
    
    def has_object_permission(self, request, view, obj):
        # If it's an admin, allow access
        if request.user and request.user.is_authenticated and request.user.role == 'admin':
            return True
        
        # Check if the object has a user attribute and it matches the request user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # For transaction objects specifically
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False


class IsAPIKeyValid(permissions.BasePermission):
    """
    Custom permission to check if API key is valid for external integrations.
    """
    
    def has_permission(self, request, view):
        # Check if request has valid API key
        api_key = request.META.get('HTTP_X_API_KEY') or request.GET.get('api_key')
        
        if not api_key:
            return False
        
        try:
            from apps.digital.models import APIKey
            api_key_obj = APIKey.objects.get(key=api_key, is_active=True)
            
            # Check if it's a sandbox key and we're in production
            if api_key_obj.is_sandbox and not request.META.get('SERVER_NAME', '').startswith('localhost'):
                return False
            
            # Check rate limits
            # This is a simplified check - in reality you'd check against Redis or similar
            if api_key_obj.current_daily_count >= api_key_obj.daily_limit:
                return False
                
            # Update usage count
            api_key_obj.current_daily_count += 1
            api_key_obj.last_used_at = request.timestamp if hasattr(request, 'timestamp') else None
            api_key_obj.save()
            
            # Store the API key user in the request for later use
            request.api_key_user = api_key_obj.user
            
            return True
        except APIKey.DoesNotExist:
            return False


class IsAgentOrAbove(permissions.BasePermission):
    """
    Custom permission to only allow agents and roles above.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.role in ['admin', 'agent', 'employee']


class IsEmployeeOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow employees or admins.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.role in ['admin', 'employee']