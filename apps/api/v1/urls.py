from django.urls import path, include
from apps.api.v1 import views

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.register, name='api-register'),
    path('auth/login/', views.login, name='api-login'),
    path('auth/refresh/', views.refresh_token, name='api-refresh'),
    path('auth/logout/', views.logout, name='api-logout'),
    
    # User endpoints
    path('users/me/', views.get_current_user, name='api-get-current-user'),
    path('users/me/', views.update_profile, name='api-update-profile'),
    path('users/change-password/', views.change_password, name='api-change-password'),
    
    # Products endpoints
    path('products/', views.list_products, name='api-list-products'),
    path('products/<str:product_id>/', views.get_product_details, name='api-get-product-details'),
    path('products/bundles/', views.list_data_bundles, name='api-list-data-bundles'),
    
    # Orders endpoints
    path('orders/', views.create_order, name='api-create-order'),
    path('orders/', views.list_orders, name='api-list-orders'),
    path('orders/<str:order_id>/', views.get_order_details, name='api-get-order-details'),
    path('orders/bulk/', views.create_bulk_order, name='api-create-bulk-order'),
    
    # Wallet endpoints
    path('wallet/', views.get_wallet_balance, name='api-get-wallet-balance'),
    path('wallet/fund/', views.fund_wallet, name='api-fund-wallet'),
    path('wallet/withdraw/', views.request_withdrawal, name='api-request-withdrawal'),
    path('wallet/transactions/', views.wallet_transaction_history, name='api-wallet-transactions'),
    
    # Payments endpoints
    path('payments/initiate/', views.initiate_payment, name='api-initiate-payment'),
    path('payments/verify/', views.verify_payment, name='api-verify-payment'),
    path('payments/webhook/', views.payment_webhook, name='api-payment-webhook'),
    
    # Agent endpoints
    path('agents/apply/', views.apply_to_become_agent, name='api-apply-agent'),
    path('agents/my-application/', views.get_agent_application_status, name='api-agent-application-status'),
    path('agents/', views.list_agents, name='api-list-agents'),
    path('agents/<str:agent_id>/approve/', views.approve_agent, name='api-approve-agent'),
    path('agents/<str:agent_id>/reject/', views.reject_agent, name='api-reject-agent'),
    
    # Transactions endpoints
    path('transactions/', views.list_transactions, name='api-list-transactions'),
    path('transactions/<str:transaction_id>/', views.get_transaction_details, name='api-get-transaction-details'),
    
    # Notifications endpoints
    path('notifications/', views.list_notifications, name='api-list-notifications'),
    path('notifications/<str:notification_id>/read/', views.mark_notification_read, name='api-mark-notification-read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='api-mark-all-notifications-read'),
    
    # Chat endpoints
    path('chat/rooms/', views.list_chat_rooms, name='api-list-chat-rooms'),
    path('chat/rooms/', views.create_chat_room, name='api-create-chat-room'),
    path('chat/rooms/<str:room_id>/messages/', views.get_room_messages, name='api-get-room-messages'),
    path('chat/messages/', views.send_message, name='api-send-message'),
    
    # Dashboard endpoints
    path('dashboard/overview/', views.dashboard_overview, name='api-dashboard-overview'),
    
    # Developer API endpoints
    path('developer/keys/', views.list_api_keys, name='api-list-api-keys'),
    path('developer/keys/', views.create_api_key, name='api-create-api-key'),
    path('developer/keys/<str:key_id>/regenerate/', views.regenerate_api_key, name='api-regenerate-api-key'),
    path('developer/keys/<str:key_id>/revoke/', views.revoke_api_key, name='api-revoke-api-key'),
    path('developer/keys/<str:key_id>/usage/', views.api_key_usage_statistics, name='api-api-key-usage'),
    path('developer/webhooks/', views.list_webhooks, name='api-list-webhooks'),
    path('developer/webhooks/', views.create_webhook, name='api-create-webhook'),
    path('developer/events/', views.list_webhook_events, name='api-list-webhook-events'),
]