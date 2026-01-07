from django.urls import path, include
from apps.api.v1 import views

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.register, name='api-register'),
    path('auth/login/', views.login, name='api-login'),
    path('auth/refresh/', views.refresh_token, name='api-refresh'),
    path('auth/logout/', views.logout, name='api-logout'),
    path('auth/password/reset/', views.password_reset, name='api-password-reset'),
    path('auth/password/reset/confirm/', views.password_reset_confirm, name='api-password-reset-confirm'),
    
    # User endpoints
    path('users/me/', views.get_current_user, name='api-get-current-user'),
    path('users/me/', views.update_profile, name='api-update-profile'),  # This should be PUT/PATCH
    path('users/change-password/', views.change_password, name='api-change-password'),
    path('users/', views.list_users, name='api-list-users'),  # For admin/employee
    path('users/<str:user_id>/', views.get_user_detail, name='api-get-user-detail'),  # For admin/employee
    path('users/<str:user_id>/', views.update_user, name='api-update-user'),  # For admin
    path('users/<str:user_id>/', views.delete_user, name='api-delete-user'),  # For admin
    path('users/<str:user_id>/suspend/', views.suspend_user, name='api-suspend-user'),  # For admin
    path('users/<str:user_id>/activate/', views.activate_user, name='api-activate-user'),  # For admin
    
    # Agent endpoints
    path('agents/apply/', views.apply_to_become_agent, name='api-apply-agent'),
    path('agents/my-application/', views.get_agent_application_status, name='api-agent-application-status'),
    path('agents/', views.list_agents, name='api-list-agents'),
    path('agents/<str:agent_id>/', views.get_agent_detail, name='api-get-agent-detail'),
    path('agents/<str:agent_id>/approve/', views.approve_agent, name='api-approve-agent'),
    path('agents/<str:agent_id>/reject/', views.reject_agent, name='api-reject-agent'),
    path('agents/<str:agent_id>/suspend/', views.suspend_agent, name='api-suspend-agent'),
    path('agents/stats/', views.agent_stats, name='api-agent-stats'),
    path('agents/tiers/', views.list_agent_tiers, name='api-list-agent-tiers'),
    path('agents/tiers/', views.create_agent_tier, name='api-create-agent-tier'),
    
    # Product endpoints
    path('products/', views.list_products, name='api-list-products'),
    path('products/<str:product_id>/', views.get_product_details, name='api-get-product-details'),
    path('products/bundles/', views.list_data_bundles, name='api-list-data-bundles'),
    path('products/', views.create_product, name='api-create-product'),  # For employee/admin
    path('products/<str:product_id>/', views.update_product, name='api-update-product'),  # For employee/admin
    path('products/<str:product_id>/', views.delete_product, name='api-delete-product'),  # For employee/admin
    path('products/<str:product_id>/toggle/', views.toggle_product, name='api-toggle-product'),  # For employee/admin
    
    # Order endpoints
    path('orders/', views.create_order, name='api-create-order'),
    path('orders/', views.list_orders, name='api-list-orders'),
    path('orders/<str:order_id>/', views.get_order_details, name='api-get-order-details'),
    path('orders/bulk/', views.create_bulk_order, name='api-create-bulk-order'),
    path('orders/<str:order_id>/status/', views.update_order_status, name='api-update-order-status'),
    path('orders/<str:order_id>/refund/', views.refund_order, name='api-refund-order'),
    path('orders/stats/', views.order_stats, name='api-order-stats'),
    
    # Wallet endpoints
    path('wallet/', views.get_wallet_balance, name='api-get-wallet-balance'),
    path('wallet/fund/', views.fund_wallet, name='api-fund-wallet'),
    path('wallet/withdraw/', views.request_withdrawal, name='api-request-withdrawal'),
    path('wallet/transactions/', views.wallet_transaction_history, name='api-wallet-transactions'),
    path('wallet/transfer/', views.transfer_wallet_funds, name='api-transfer-wallet-funds'),
    path('wallet/<str:wallet_id>/adjust/', views.adjust_wallet_balance, name='api-adjust-wallet-balance'),
    
    # Payment endpoints
    path('payments/initiate/', views.initiate_payment, name='api-initiate-payment'),
    path('payments/verify/', views.verify_payment, name='api-verify-payment'),
    path('payments/webhook/', views.payment_webhook, name='api-payment-webhook'),
    path('payments/', views.list_payments, name='api-list-payments'),
    path('payments/<str:payment_id>/', views.get_payment_details, name='api-get-payment-details'),
    path('payments/<str:payment_id>/refund/', views.refund_payment, name='api-refund-payment'),
    
    # Transaction endpoints
    path('transactions/', views.list_transactions, name='api-list-transactions'),
    path('transactions/<str:transaction_id>/', views.get_transaction_details, name='api-get-transaction-details'),
    path('transactions/export/', views.export_transactions, name='api-export-transactions'),
    
    # Notifications endpoints
    path('notifications/', views.list_notifications, name='api-list-notifications'),
    path('notifications/<str:notification_id>/', views.get_notification_detail, name='api-get-notification-detail'),
    path('notifications/<str:notification_id>/read/', views.mark_notification_read, name='api-mark-notification-read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='api-mark-all-notifications-read'),
    path('notifications/send/', views.send_notification, name='api-send-notification'),
    path('notifications/broadcast/', views.broadcast_notification, name='api-broadcast-notification'),
    
    # Chat endpoints
    path('chat/rooms/', views.list_chat_rooms, name='api-list-chat-rooms'),
    path('chat/rooms/', views.create_chat_room, name='api-create-chat-room'),
    path('chat/rooms/<str:room_id>/', views.get_chat_room_detail, name='api-get-chat-room-detail'),
    path('chat/rooms/<str:room_id>/messages/', views.get_room_messages, name='api-get-room-messages'),
    path('chat/messages/', views.send_message, name='api-send-message'),
    path('chat/rooms/<str:room_id>/close/', views.close_chat_room, name='api-close-chat-room'),
    path('chat/rooms/<str:room_id>/assign/', views.assign_chat_room, name='api-assign-chat-room'),
    
    # CMS endpoints
    path('cms/pages/', views.list_cms_pages, name='api-list-cms-pages'),
    path('cms/pages/<slug:slug>/', views.get_cms_page, name='api-get-cms-page'),
    path('cms/pages/', views.create_cms_page, name='api-create-cms-page'),
    path('cms/pages/<slug:slug>/', views.update_cms_page, name='api-update-cms-page'),
    path('cms/pages/<slug:slug>/', views.delete_cms_page, name='api-delete-cms-page'),
    path('cms/pages/<slug:slug>/publish/', views.publish_cms_page, name='api-publish-cms-page'),
    path('cms/settings/', views.get_cms_settings, name='api-get-cms-settings'),
    path('cms/settings/', views.update_cms_settings, name='api-update-cms-settings'),
    
    # Dashboard endpoints
    path('dashboard/overview/', views.dashboard_overview, name='api-dashboard-overview'),
    path('dashboard/stats/', views.dashboard_stats, name='api-dashboard-stats'),
    path('dashboard/charts/', views.dashboard_charts, name='api-dashboard-charts'),
    path('dashboard/admin/', views.admin_dashboard, name='api-admin-dashboard'),
    path('dashboard/system/', views.system_dashboard, name='api-system-dashboard'),
    
    # Reports endpoints
    path('reports/revenue/', views.revenue_report, name='api-revenue-report'),
    path('reports/transactions/', views.transactions_report, name='api-transactions-report'),
    path('reports/agents/', views.agents_report, name='api-agents-report'),
    path('reports/generate/', views.generate_report, name='api-generate-report'),
    path('reports/export/', views.export_report, name='api-export-report'),
    path('reports/schedules/', views.report_schedules, name='api-report-schedules'),
    
    # Audit endpoints
    path('audit/logs/', views.audit_logs, name='api-audit-logs'),
    path('audit/logs/<str:log_id>/', views.audit_log_detail, name='api-audit-log-detail'),
    path('audit/logs/summary/', views.audit_summary, name='api-audit-summary'),
    path('audit/login-attempts/', views.login_attempts_audit, name='api-login-attempts-audit'),
    path('audit/security/', views.security_audit, name='api-security-audit'),
    
    # Developer API endpoints
    path('developer/keys/', views.list_api_keys, name='api-list-api-keys'),
    path('developer/keys/', views.create_api_key, name='api-create-api-key'),
    path('developer/keys/<str:key_id>/', views.get_api_key_detail, name='api-get-api-key-detail'),
    path('developer/keys/<str:key_id>/', views.update_api_key, name='api-update-api-key'),
    path('developer/keys/<str:key_id>/', views.delete_api_key, name='api-delete-api-key'),
    path('developer/keys/<str:key_id>/regenerate/', views.regenerate_api_key, name='api-regenerate-api-key'),
    path('developer/keys/<str:key_id>/revoke/', views.revoke_api_key, name='api-revoke-api-key'),
    path('developer/keys/<str:key_id>/usage/', views.api_key_usage_statistics, name='api-api-key-usage'),
    path('developer/webhooks/', views.list_webhooks, name='api-list-webhooks'),
    path('developer/webhooks/', views.create_webhook, name='api-create-webhook'),
    path('developer/overview/', views.developer_overview, name='api-developer-overview'),
    path('developer/events/', views.list_webhook_events, name='api-list-webhook-events'),
]