"""
Enhanced URL Configuration for Vintage Ecommerce
Includes all new advanced features and endpoints
"""

from django.urls import path, include
from store import views
from store import views_enhanced
from store import inventory_management
from store import analytics_engine
from store import customer_engagement
from store import vendor_management

app_name = 'store'

# Main store URLs
urlpatterns = [
    # Core store views
    path('', views.index, name='index'),
    path('shop/', views_enhanced.enhanced_shop, name='shop'),
    path('product/<slug:slug>/', views_enhanced.product_detail_enhanced, name='product_detail'),
    path('category/<int:category_id>/', views.category, name='category'),
    path('search/', views_enhanced.advanced_search, name='search'),
    
    # Cart and Checkout
    path('cart/', views.cart, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/verify/', views.paystack_payment_verify, name='payment_verify'),
    
    # Enhanced Features
    path('wishlist/', views_enhanced.wishlist, name='wishlist'),
    path('wishlist/toggle/', views_enhanced.add_to_wishlist, name='toggle_wishlist'),
    path('comparison/', views_enhanced.product_comparison, name='comparison'),
    path('comparison/add/', views_enhanced.add_to_comparison, name='add_to_comparison'),
    path('quick-view/', views_enhanced.quick_view, name='quick_view'),
    
    # Flash Sales
    path('flash-sales/', views_enhanced.flash_sales, name='flash_sales'),
    path('flash-sale/<int:sale_id>/', views_enhanced.flash_sale_detail, name='flash_sale_detail'),
    
    # Bundles
    path('bundles/', views_enhanced.bundles, name='bundles'),
    path('bundle/<int:bundle_id>/', views_enhanced.bundle_detail, name='bundle_detail'),
    
    # Customer Features
    path('dashboard/', customer_engagement.personalized_dashboard, name='customer_dashboard'),
    path('loyalty/', views_enhanced.loyalty_dashboard, name='loyalty_dashboard'),
    path('notifications/', views_enhanced.notifications, name='notifications'),
    path('recommendations/', customer_engagement.product_recommendations_api, name='recommendations_api'),
    
    # Email tracking
    path('email/open/<int:user_id>/<str:campaign_id>/', customer_engagement.track_email_open, name='track_email_open'),
    path('email/click/<int:user_id>/<str:campaign_id>/', customer_engagement.track_email_click, name='track_email_click'),
    
    # Reviews
    path('reviews/add/', views.add_review, name='add_review'),
    
    # Analytics API
    path('api/analytics/', analytics_engine.analytics_api, name='analytics_api'),
]

# Vendor URLs
vendor_patterns = [
    # Vendor Dashboard
    path('dashboard/', vendor_management.vendor_dashboard, name='vendor_dashboard'),
    path('analytics/', vendor_management.vendor_analytics_dashboard, name='vendor_analytics'),
    
    # Product Management
    path('products/', views.vendor_products, name='vendor_products'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    
    # Inventory Management
    path('inventory/', inventory_management.inventory_dashboard, name='inventory_dashboard'),
    path('inventory/update-stock/', inventory_management.update_product_stock, name='update_stock'),
    path('inventory/alert/<int:alert_id>/resolve/', inventory_management.resolve_inventory_alert, name='resolve_alert'),
    
    # Orders
    path('orders/', views.vendor_orders, name='vendor_orders'),
    path('orders/<str:order_id>/', views.vendor_order_detail, name='vendor_order_detail'),
    path('orders/<str:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    
    # Commission and Earnings
    path('commissions/', vendor_management.vendor_commission_report, name='commission_report'),
    path('earnings/', views.vendor_earnings, name='vendor_earnings'),
    
    # Vendor Profile
    path('profile/', views.vendor_profile, name='vendor_profile'),
    path('profile/edit/', views.edit_vendor_profile, name='edit_vendor_profile'),
    
    # Notifications
    path('notifications/', views.vendor_notifications, name='vendor_notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
]

# Admin URLs (for staff users)
admin_patterns = [
    # Admin Analytics
    path('analytics/', analytics_engine.admin_analytics_dashboard, name='admin_analytics'),
    
    # Vendor Management
    path('vendors/', views.admin_vendors, name='admin_vendors'),
    path('vendors/<int:vendor_id>/verify/', views.verify_vendor, name='verify_vendor'),
    path('vendors/<int:vendor_id>/suspend/', views.suspend_vendor, name='suspend_vendor'),
    
    # Product Management
    path('products/', views.admin_products, name='admin_products'),
    path('products/<int:product_id>/approve/', views.approve_product, name='approve_product'),
    path('products/<int:product_id>/reject/', views.reject_product, name='reject_product'),
    
    # Order Management
    path('orders/', views.admin_orders, name='admin_orders'),
    path('orders/<str:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    
    # Commission Management
    path('commissions/', views.admin_commissions, name='admin_commissions'),
    path('commissions/<int:commission_id>/approve/', views.approve_commission, name='approve_commission'),
    path('commissions/payout/', views.process_vendor_payout, name='process_payout'),
    
    # Reports
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/inventory/', views.inventory_report, name='inventory_report'),
    path('reports/vendors/', views.vendor_performance_report, name='vendor_report'),
    
    # System Settings
    path('settings/', views.admin_settings, name='admin_settings'),
    path('settings/categories/', views.manage_categories, name='manage_categories'),
    path('settings/brands/', views.manage_brands, name='manage_brands'),
    path('settings/flash-sales/', views.manage_flash_sales, name='manage_flash_sales'),
]

# API URLs for AJAX requests
api_patterns = [
    # Product APIs
    path('products/search/', views.product_search_api, name='product_search_api'),
    path('products/<int:product_id>/variants/', views.product_variants_api, name='product_variants_api'),
    path('products/recommendations/', customer_engagement.product_recommendations_api, name='product_recommendations_api'),
    
    # Cart APIs
    path('cart/count/', views.cart_count_api, name='cart_count_api'),
    path('cart/items/', views.cart_items_api, name='cart_items_api'),
    
    # Wishlist APIs
    path('wishlist/count/', views.wishlist_count_api, name='wishlist_count_api'),
    path('wishlist/items/', views.wishlist_items_api, name='wishlist_items_api'),
    
    # Analytics APIs
    path('analytics/sales/', analytics_engine.analytics_api, name='sales_analytics_api'),
    path('analytics/products/', analytics_engine.analytics_api, name='product_analytics_api'),
    path('analytics/customers/', analytics_engine.analytics_api, name='customer_analytics_api'),
    
    # Inventory APIs
    path('inventory/alerts/', views.inventory_alerts_api, name='inventory_alerts_api'),
    path('inventory/movements/', views.stock_movements_api, name='stock_movements_api'),
    
    # Notification APIs
    path('notifications/unread-count/', views.unread_notifications_count, name='unread_notifications_count'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]

# Include all URL patterns
urlpatterns += [
    path('vendor/', include((vendor_patterns, 'vendor'))),
    path('admin-panel/', include((admin_patterns, 'admin_panel'))),
    path('api/', include((api_patterns, 'api'))),
]

# Additional utility URLs
utility_patterns = [
    # File uploads
    path('upload/image/', views.upload_image, name='upload_image'),
    path('upload/document/', views.upload_document, name='upload_document'),
    
    # Export/Import
    path('export/products/', views.export_products, name='export_products'),
    path('import/products/', views.import_products, name='import_products'),
    path('export/orders/', views.export_orders, name='export_orders'),
    
    # Bulk operations
    path('bulk/update-prices/', views.bulk_update_prices, name='bulk_update_prices'),
    path('bulk/update-stock/', views.bulk_update_stock, name='bulk_update_stock'),
    path('bulk/delete-products/', views.bulk_delete_products, name='bulk_delete_products'),
    
    # System utilities
    path('clear-cache/', views.clear_cache, name='clear_cache'),
    path('generate-sitemap/', views.generate_sitemap, name='generate_sitemap'),
    path('health-check/', views.health_check, name='health_check'),
]

urlpatterns += utility_patterns

# Error handling URLs
handler404 = 'store.views.custom_404'
handler500 = 'store.views.custom_500'
handler403 = 'store.views.custom_403'