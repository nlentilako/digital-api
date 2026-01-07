from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'employee'


class IsAgent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'agent'


class IsDeveloper(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'developer'


class IsAdminOrEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'employee']


class IsAdminOrAgent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'agent']


class IsAdminOrEmployeeOrAgent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'employee', 'agent']


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'id') and hasattr(request, 'user') and hasattr(obj, '__class__'):
            # For cases where object is a user instance
            if hasattr(obj, '__class__') and obj.__class__.__name__ == 'User':
                return obj.id == request.user.id
        return False


class IsOwnerOrAdminOrEmployee(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'employee']:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsOwnerOrAdminOrEmployeeOrAgent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'employee', 'agent']:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsOwnerOrAdminOrAgent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'agent']:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsUserOrAbove(permissions.BasePermission):
    """Allow access to users and all roles above"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            'user', 'agent', 'employee', 'admin', 'developer'
        ]


class IsAgentOrAbove(permissions.BasePermission):
    """Allow access to agents and all roles above"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            'agent', 'employee', 'admin', 'developer'
        ]


class IsEmployeeOrAbove(permissions.BasePermission):
    """Allow access to employees and all roles above"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            'employee', 'admin'
        ]


class IsAdminOrAbove(permissions.BasePermission):
    """Allow access to admins and all roles above (only admin)"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            'admin'
        ]


class IsDeveloperOrAbove(permissions.BasePermission):
    """Allow access to developers and all roles above"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            'developer', 'admin'
        ]


class IsPublic(permissions.BasePermission):
    """Allow public access - no authentication required"""
    def has_permission(self, request, view):
        return True


class IsAuthenticatedOrPublicAPI(permissions.BasePermission):
    """For endpoints that allow both authenticated users and API key access"""
    def has_permission(self, request, view):
        # Check if user is authenticated normally
        if request.user.is_authenticated:
            return True
        
        # Check if it's an API key request (for developer access)
        api_key = request.META.get('HTTP_X_API_KEY') or request.GET.get('api_key')
        if api_key:
            # This would be checked in the view or by a decorator
            return True
        
        return False


class CanViewPublishedCMS(permissions.BasePermission):
    """Permission for viewing published CMS content"""
    def has_permission(self, request, view):
        if view.action == 'list' or view.action == 'retrieve':
            return request.user.is_authenticated and request.user.role in [
                'user', 'agent', 'employee', 'admin'
            ]
        return request.user.is_authenticated and request.user.role in [
            'employee', 'admin'
        ]


class CanManageCMS(permissions.BasePermission):
    """Permission for managing CMS content"""
    def has_permission(self, request, view):
        if view.action in ['create', 'update', 'partial_update', 'destroy']:
            return request.user.is_authenticated and request.user.role in [
                'employee', 'admin'
            ]
        return request.user.is_authenticated and request.user.role in [
            'user', 'agent', 'employee', 'admin'
        ]


class CanViewAllOrders(permissions.BasePermission):
    """Permission to view all orders (for employees and above)"""
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            if request.user.role in ['employee', 'admin']:
                return True
            elif request.user.role in ['agent', 'user', 'developer']:
                return False  # These roles can only view their own
        return request.user.is_authenticated


class CanManageOrders(permissions.BasePermission):
    """Permission to manage orders (change status, refund)"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            'employee', 'admin'
        ]


class CanManageUsers(permissions.BasePermission):
    """Permission to manage users (for admins)"""
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return request.user.is_authenticated and request.user.role in [
                'employee', 'admin'
            ]
        elif view.action in ['update', 'partial_update', 'destroy']:
            return request.user.is_authenticated and request.user.role in [
                'admin'
            ]
        return False


class CanManageAgents(permissions.BasePermission):
    """Permission to manage agents"""
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return request.user.is_authenticated and request.user.role in [
                'employee', 'admin'
            ]
        elif view.action in ['approve', 'reject', 'suspend']:
            return request.user.is_authenticated and request.user.role in [
                'employee', 'admin'
            ]
        return request.user.is_authenticated


class CanManageProducts(permissions.BasePermission):
    """Permission to manage products"""
    def has_permission(self, request, view):
        if view.action in ['create', 'update', 'partial_update', 'destroy', 'toggle']:
            return request.user.is_authenticated and request.user.role in [
                'employee', 'admin'
            ]
        return request.user.is_authenticated


class CanManageWallet(permissions.BasePermission):
    """Permission to manage wallets"""
    def has_permission(self, request, view):
        if view.action in ['adjust', 'transfer']:
            # Only admin can adjust any wallet or transfer between users
            return request.user.is_authenticated and request.user.role == 'admin'
        elif view.action in ['withdraw']:
            # Only agents can withdraw
            return request.user.is_authenticated and request.user.role == 'agent'
        else:
            # Users and agents can view own wallet, admin can view all
            if request.user.role in ['admin']:
                return True
            elif request.user.role in ['user', 'agent']:
                return True  # Will be further restricted by object permission
        return request.user.is_authenticated


class CanManageNotifications(permissions.BasePermission):
    """Permission to manage notifications"""
    def has_permission(self, request, view):
        if view.action in ['send', 'broadcast']:
            return request.user.is_authenticated and request.user.role in [
                'employee', 'admin'
            ]
        return request.user.is_authenticated


class CanManageChat(permissions.BasePermission):
    """Permission to manage chat"""
    def has_permission(self, request, view):
        if view.action in ['close', 'assign']:
            return request.user.is_authenticated and request.user.role in [
                'employee', 'admin'
            ]
        return request.user.is_authenticated


class CanViewReports(permissions.BasePermission):
    """Permission to view reports"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            'employee', 'admin'
        ]


class CanViewAuditLogs(permissions.BasePermission):
    """Permission to view audit logs"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class CanManageDeveloperAPI(permissions.BasePermission):
    """Permission to manage developer API keys"""
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve'] and request.user.role == 'admin':
            return True  # Admin can view all API keys
        elif view.action in ['create', 'update', 'partial_update', 'destroy', 'regenerate', 'revoke', 'usage']:
            # Developer can manage their own keys, admin can manage all
            return request.user.is_authenticated and request.user.role in ['developer', 'admin']
        elif view.action in ['overview', 'events']:
            return request.user.is_authenticated and request.user.role in ['developer', 'admin']
        return False