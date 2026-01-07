from django.urls import path
from apps.digital.views import purchase_views, webhook_views, admin_views

urlpatterns = [
    # Purchase endpoints
    path('purchase/', purchase_views.initiate_purchase, name='initiate-purchase'),
    path('transactions/', purchase_views.list_transactions, name='list-transactions'),
    path('transaction/<str:transaction_id>/', purchase_views.get_transaction_status, name='transaction-status'),
    path('transaction/<str:transaction_id>/retry/', purchase_views.retry_transaction, name='retry-transaction'),
    
    # Webhook endpoints
    path('webhooks/mtn/', webhook_views.mtn_webhook, name='mtn-webhook'),
    path('webhooks/vodafone/', webhook_views.vodafone_webhook, name='vodafone-webhook'),
    path('webhooks/airteltigo/', webhook_views.airteltigo_webhook, name='airteltigo-webhook'),
    
    # Admin endpoints
    path('admin/service-types/', admin_views.manage_service_types, name='manage-service-types'),
    path('admin/network-providers/', admin_views.manage_network_providers, name='manage-network-providers'),
    path('admin/products/', admin_views.manage_digital_products, name='manage-digital-products'),
    path('admin/products/<str:product_id>/', admin_views.manage_digital_product, name='manage-digital-product'),
    path('admin/service-types/<str:service_type_id>/toggle/', admin_views.toggle_service_availability, name='toggle-service-availability'),
    path('admin/products/<str:product_id>/toggle/', admin_views.toggle_product_availability, name='toggle-product-availability'),
    path('admin/transactions/', admin_views.admin_transactions, name='admin-transactions'),
    path('admin/users/<str:user_id>/pricing/', admin_views.user_pricing_management, name='user-pricing-management'),
]