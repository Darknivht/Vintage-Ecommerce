from django.urls import path
from store import views
from store import views_enhanced

app_name = "store"

urlpatterns = [
    # Main Pages
    path("", views.index, name="index"),
    path("shop/", views.shop, name="shop"),
    path("category/<id>/", views.category, name="category"),
    path('get-subcategories/', views.get_subcategories, name='get_subcategories'),
    path("detail/<slug>/", views.product_detail, name="product_detail"),
    
    # Cart & Orders
    path("cart/", views.cart, name="cart"),
    path("create_order/", views.create_order, name="create_order"),
    path("checkout/<order_id>/", views.checkout, name="checkout"),
    path("coupon_apply/<order_id>/", views.coupon_apply, name="coupon_apply"),
    path("payment_status/<order_id>/", views.payment_status, name="payment_status"),

    # Listings
    path("listing/create/", views.create_listing, name="create_listing"),
    path("listing/edit/<int:listing_id>/", views.edit_listing, name="edit_listing"),
    path("listing/delete/<int:listing_id>/", views.delete_listing, name="delete_listing"),
    path("listing/toggle-status/<int:listing_id>/", views.toggle_listing_status, name="toggle_listing_status"),
    path("listing/<slug:slug>/", views.listing_detail, name="listing_detail"),
    path("listings/", views.browse_listings, name="browse_listings"),
    path("vendor/listings/", views.vendor_listings, name="vendor_listings"),
    path("vendor/listing-inquiries/", views.listing_inquiries, name="listing_inquiries"),
    path("vendor/inquiry/mark-read/<int:inquiry_id>/", views.mark_inquiry_read, name="mark_inquiry_read"),

    # Legacy Cart Operations
    path("filter_products/", views.filter_products, name="filter_products"),
    path("add_to_cart/", views.add_to_cart, name="add_to_cart"),
    path("add-to-cart/", views.add_to_cart, name="add_to_cart_hyphen"),  # Hyphenated alias
    path("store/add-to-cart/", views.add_to_cart, name="add_to_cart_store"),  # Handle /store/add-to-cart/
    path("delete_cart_item/", views.delete_cart_item, name="delete_cart_item"),

    # Modern AJAX Operations
    path("ajax/add-to-cart/", views.add_to_cart_ajax, name="add_to_cart_ajax"),
    path("ajax/update-cart/", views.update_cart_ajax, name="update_cart_ajax"),
    path("ajax/toggle-wishlist/", views.toggle_wishlist_ajax, name="toggle_wishlist_ajax"),
    path("ajax/product-quick-view/<int:product_id>/", views.product_quick_view, name="product_quick_view"),
    path("ajax/search-suggestions/", views.search_suggestions, name="search_suggestions"),
    path("ajax/toggle-comparison/", views.toggle_comparison, name="toggle_comparison"),
    path("ajax/clear-comparison/", views.clear_comparison, name="clear_comparison"),
    
    # Listing AJAX Operations  
    path("ajax/toggle-listing-favorite/", views.toggle_listing_favorite, name="toggle_listing_favorite"),
    path("ajax/get-subcategories/", views.get_subcategories, name="get_subcategories"),
    
    # Product Comparison
    path("comparison/", views.comparison_view, name="comparison"),
    path("ajax/toggle-comparison/", views.toggle_comparison, name="toggle_comparison"),
    path("ajax/clear-comparison/", views.clear_comparison, name="clear_comparison"),
    
    # Product Comparison
    path("comparison/", views.comparison_view, name="comparison"),

    # Brands
    path("brands/", views.brands_list, name="brands_list"),
    path("brand/<slug:slug>/", views.brand_products, name="brand_products"),

    # Flash Sales
    path("flash-sales/", views.flash_sales, name="flash_sales"),
    path("flash-sale/<int:id>/", views.flash_sale_detail, name="flash_sale_detail"),

    # Payment Processing
    path('stripe_payment/<order_id>/', views.stripe_payment, name='stripe_payment'),
    path('stripe_payment_verify/<order_id>/', views.stripe_payment_verify, name='stripe_payment_verify'),
    path('paypal_payment_verify/<order_id>/', views.paypal_payment_verify, name='paypal_payment_verify'),
    path('razorpay_payment_verify/<order_id>/', views.razorpay_payment_verify, name='razorpay_payment_verify'),
    path('paystack_payment_verify/<order_id>/', views.paystack_payment_verify, name='paystack_payment_verify'),
    path('flutterwave_payment_callback/<order_id>/', views.flutterwave_payment_callback, name='flutterwave_payment_callback'),

    # Order Tracking
    path("order_tracker_page/", views.order_tracker_page, name="order_tracker_page"),
    path("order_tracker_detail/<item_id>/", views.order_tracker_detail, name="order_tracker_detail"),

    # Dashboard Routing
    path("dashboard/", views.dashboard_redirect, name="dashboard_redirect"),
    
    # Review System
    path("product/<slug:product_slug>/review/", views.submit_review, name="submit_review"),
    path("product/<slug:product_slug>/reviews/", views.product_reviews, name="product_reviews"),
    path("ajax/submit-review/", views.ajax_submit_review, name="ajax_submit_review"),

    # Static Pages
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("faqs/", views.faqs, name="faqs"),
    path("privacy_policy/", views.privacy_policy, name="privacy_policy"),
    path("terms_conditions/", views.terms_conditions, name="terms_conditions"),

]