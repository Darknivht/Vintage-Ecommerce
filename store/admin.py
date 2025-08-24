from django.contrib import admin
from store import models as store_models
from store.forms import ListingForm

# === Inlines ===
class GalleryInline(admin.TabularInline):
    model = store_models.Gallery

class VariantInline(admin.TabularInline):
    model = store_models.Variant

class VariantItemInline(admin.TabularInline):
    model = store_models.VariantItem


# === Category & Schema ===
class CategorySchemaInline(admin.StackedInline):
    model = store_models.CategorySchema
    extra = 0

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'parent', 'image']
    list_editable = ['type', 'image']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ['type', 'parent']
    search_fields = ['title']



# === Product Admin ===
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'regular_price', 'stock', 'status', 'featured', 'vendor', 'date']
    search_fields = ['name', 'category__title']
    list_filter = ['status', 'featured', 'category']
    inlines = [GalleryInline, VariantInline]
    prepopulated_fields = {'slug': ('name',)}


# === Variant Admins ===
class VariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'name']
    search_fields = ['product__name', 'name']
    inlines = [VariantItemInline]

class VariantItemAdmin(admin.ModelAdmin):
    list_display = ['variant', 'title', 'content']
    search_fields = ['variant__name', 'title']


# === Other Admins ===
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['product', 'gallery_id']
    search_fields = ['product__name', 'gallery_id']

class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'product', 'user', 'qty', 'price', 'total', 'date']
    search_fields = ['cart_id', 'product__name', 'user__username']
    list_filter = ['date', 'product']

class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'vendor', 'discount']
    search_fields = ['code', 'vendor__username']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'customer', 'total', 'payment_status', 'order_status', 'payment_method', 'date']
    list_editable = ['payment_status', 'order_status', 'payment_method']
    search_fields = ['order_id', 'customer__username']
    list_filter = ['payment_status', 'order_status']

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['item_id', 'order', 'product', 'qty', 'price', 'total']
    search_fields = ['item_id', 'order__order_id', 'product__name']
    list_filter = ['order__date']

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'active', 'date']
    search_fields = ['user__username', 'product__name']
    list_filter = ['active', 'rating']


# === Enhanced Listing Admin ===
class ListingImageInline(admin.TabularInline):
    model = store_models.ListingImage
    extra = 1
    fields = ['image', 'caption', 'order', 'is_main']


class ListingAdmin(admin.ModelAdmin):
    inlines = [ListingImageInline]
    list_display = [
        'title', 'vendor', 'category', 'listing_type', 'status', 
        'price', 'location', 'views_count', 'contact_count', 
        'featured', 'urgent', 'created_at'
    ]
    list_filter = [
        'status', 'listing_type', 'category', 'featured', 
        'urgent', 'promoted', 'created_at'
    ]
    search_fields = [
        'title', 'vendor__username', 'location', 'tags',
        'short_description', 'description'
    ]
    readonly_fields = [
        'slug', 'created_at', 'updated_at', 'views_count', 
        'contact_count', 'favorites_count'
    ]
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 'vendor', 'category', 'subcategory', 'listing_type'
            )
        }),
        ('Content', {
            'fields': (
                'short_description', 'description', 'tags'
            )
        }),
        ('Pricing & Availability', {
            'fields': (
                'price', 'price_type', 'available_from', 'available_until'
            )
        }),
        ('Location & Contact', {
            'fields': (
                'location', 'address', 'latitude', 'longitude',
                'contact_phone', 'contact_email'
            )
        }),
        ('Media', {
            'fields': (
                'image', 'gallery_images', 'video_url'
            )
        }),
        ('SEO', {
            'fields': (
                'meta_title', 'meta_description'
            ),
            'classes': ['collapse']
        }),
        ('Status & Visibility', {
            'fields': (
                'status', 'featured', 'promoted', 'urgent',
                'expires_at'
            )
        }),
        ('Analytics', {
            'fields': (
                'views_count', 'contact_count', 'favorites_count'
            ),
            'classes': ['collapse']
        }),
        ('System', {
            'fields': (
                'slug', 'created_at', 'updated_at', 'custom_fields', 'extra_data'
            ),
            'classes': ['collapse']
        })
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'vendor', 'category', 'subcategory'
        )


class ListingInquiryAdmin(admin.ModelAdmin):
    list_display = [
        'listing', 'inquirer_name', 'inquirer_email', 
        'is_read', 'created_at'
    ]
    list_filter = ['is_read', 'created_at', 'listing__category']
    search_fields = [
        'inquirer_name', 'inquirer_email', 'listing__title', 'message'
    ]
    readonly_fields = ['created_at', 'response_date']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Inquiry Details', {
            'fields': (
                'listing', 'inquirer_name', 'inquirer_email', 
                'inquirer_phone', 'message', 'created_at'
            )
        }),
        ('Response', {
            'fields': (
                'is_read', 'vendor_response', 'response_date'
            )
        })
    )


class ListingFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'listing', 'created_at']
    list_filter = ['created_at', 'listing__category']
    search_fields = ['user__username', 'listing__title']
    date_hierarchy = 'created_at'

# === Enhanced Model Admins ===

# Brand Admin
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_featured', 'created_at']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

# Product Attribute Admin
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'attribute_type', 'is_required']
    list_filter = ['attribute_type', 'is_required']
    search_fields = ['name', 'display_name']

class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['product', 'attribute', 'value']
    list_filter = ['attribute']
    search_fields = ['product__name', 'attribute__name', 'value']

# Flash Sale Admin
class FlashSaleItemInline(admin.TabularInline):
    model = store_models.FlashSaleItem
    extra = 1

class FlashSaleAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount_percentage', 'start_date', 'end_date', 'is_active', 'is_live']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['name', 'description']
    inlines = [FlashSaleItemInline]
    
    def is_live(self, obj):
        return obj.is_live()
    is_live.boolean = True
    is_live.short_description = 'Currently Live'

class FlashSaleItemAdmin(admin.ModelAdmin):
    list_display = ['flash_sale', 'product', 'sale_price', 'quantity_limit', 'sold_quantity']
    list_filter = ['flash_sale']
    search_fields = ['flash_sale__name', 'product__name']

# Bundle Admin
class BundleItemInline(admin.TabularInline):
    model = store_models.BundleItem
    extra = 1

class BundleAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount_percentage', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    inlines = [BundleItemInline]

# Loyalty Program Admin
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'points_per_dollar', 'min_points_to_redeem', 'point_value', 'is_active']
    list_filter = ['is_active']

class CustomerLoyaltyAccountAdmin(admin.ModelAdmin):
    list_display = ['customer', 'total_points', 'lifetime_points', 'tier']
    list_filter = ['tier']
    search_fields = ['customer__username', 'customer__email']
    readonly_fields = ['lifetime_points']

class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'transaction_type', 'points', 'description', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['account__customer__username', 'description']

# Wishlist Admin
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'product__name']

# Recently Viewed Admin
class RecentlyViewedAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['user__username', 'product__name']

# Product Comparison Admin
class ProductComparisonAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    filter_horizontal = ['products']

# Notification Admin
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'title', 'message']

# === Register Everything ===
admin.site.register(store_models.Category, CategoryAdmin)
admin.site.register(store_models.CategorySchema)
admin.site.register(store_models.Product, ProductAdmin)
admin.site.register(store_models.Variant, VariantAdmin)
admin.site.register(store_models.VariantItem, VariantItemAdmin)
admin.site.register(store_models.Gallery, GalleryAdmin)
admin.site.register(store_models.Cart, CartAdmin)
admin.site.register(store_models.Coupon, CouponAdmin)
admin.site.register(store_models.Order, OrderAdmin)
admin.site.register(store_models.OrderItem, OrderItemAdmin)
admin.site.register(store_models.Review, ReviewAdmin)

# Enhanced Listing Models
admin.site.register(store_models.Listing, ListingAdmin)
admin.site.register(store_models.ListingImage)
admin.site.register(store_models.ListingFavorite, ListingFavoriteAdmin)
admin.site.register(store_models.ListingInquiry, ListingInquiryAdmin)

# Register new models
admin.site.register(store_models.Brand, BrandAdmin)
admin.site.register(store_models.ProductAttribute, ProductAttributeAdmin)
admin.site.register(store_models.ProductAttributeValue, ProductAttributeValueAdmin)
admin.site.register(store_models.FlashSale, FlashSaleAdmin)
admin.site.register(store_models.FlashSaleItem, FlashSaleItemAdmin)
admin.site.register(store_models.Bundle, BundleAdmin)
admin.site.register(store_models.BundleItem)
admin.site.register(store_models.LoyaltyProgram, LoyaltyProgramAdmin)
admin.site.register(store_models.CustomerLoyaltyAccount, CustomerLoyaltyAccountAdmin)
admin.site.register(store_models.PointTransaction, PointTransactionAdmin)
admin.site.register(store_models.WishlistItem, WishlistItemAdmin)
admin.site.register(store_models.RecentlyViewed, RecentlyViewedAdmin)
admin.site.register(store_models.ProductComparison, ProductComparisonAdmin)
admin.site.register(store_models.NotificationType, NotificationTypeAdmin)
admin.site.register(store_models.Notification, NotificationAdmin)
