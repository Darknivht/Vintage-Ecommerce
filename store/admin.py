from django.contrib import admin
from store import models as store_models

class GalleryInline(admin.TabularInline):
    model = store_models.Gallery

class VariantInline(admin.TabularInline):
    model = store_models.Variant

class VariantItemInline(admin.TabularInline):
    model = store_models.VariantItem

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_parent_display', 'get_level_display', 'order', 'is_featured', 'image']
    list_editable = ['order', 'is_featured', 'image']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ['parent', 'is_featured']
    search_fields = ['title', 'description']
    readonly_fields = ['get_full_path']
    change_list_template = 'admin/store/category/change_list.html'
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'parent', 'description')
        }),
        ('Display Options', {
            'fields': ('image', 'icon', 'order', 'is_featured')
        }),
        ('Hierarchy Information', {
            'fields': ('get_full_path',),
            'classes': ('collapse',)
        }),
    )
    
    def get_parent_display(self, obj):
        return obj.parent.title if obj.parent else '-'
    get_parent_display.short_description = 'Parent'
    
    def get_level_display(self, obj):
        level = 0
        parent = obj.parent
        while parent:
            level += 1
            parent = parent.parent
        return level
    get_level_display.short_description = 'Level'
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Get all categories in a hierarchical structure
        categories = []
        
        # First get all top-level categories
        top_categories = store_models.Category.objects.filter(parent__isnull=True).order_by('order', 'title')
        
        # Helper function to add categories recursively
        def add_categories_recursively(category_list, parent=None, level=0):
            for category in store_models.Category.objects.filter(parent=parent).order_by('order', 'title'):
                category.level = level
                category_list.append(category)
                add_categories_recursively(category_list, category, level + 1)
        
        # Add all categories recursively
        for category in top_categories:
            category.level = 0
            categories.append(category)
            add_categories_recursively(categories, category, 1)
        
        extra_context['categories'] = categories
        return super().changelist_view(request, extra_context=extra_context)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'regular_price', 'stock', 'status', 'featured', 'vendor', 'date']
    search_fields = ['name', 'category__title']
    list_filter = ['status', 'featured', 'category']
    inlines = [GalleryInline, VariantInline]
    prepopulated_fields = {'slug': ('name',)}

class VariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'name']
    search_fields = ['product__name', 'name']
    inlines = [VariantItemInline]
    
class VariantItemAdmin(admin.ModelAdmin):
    list_display = ['variant', 'title', 'content']
    search_fields = ['variant__name', 'title']

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

class RealEstateListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'state', 'local_government', 'neighborhood', 'price', 'vendor', 'status', 'date_posted']
    list_filter = ['status', 'state', 'local_government', 'category']
    search_fields = ['title', 'description', 'state', 'local_government', 'neighborhood']
    prepopulated_fields = {'slug': ('title',)}

class VehicleListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'brand', 'vehicle_type', 'price', 'year', 'vendor', 'status', 'date_posted']
    list_filter = ['status', 'brand', 'vehicle_type', 'category']
    search_fields = ['title', 'description', 'brand']
    prepopulated_fields = {'slug': ('title',)}

class JobListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'company', 'location', 'job_type', 'vendor', 'status', 'date_posted']
    list_filter = ['status', 'job_type', 'category']
    search_fields = ['title', 'description', 'company', 'location']
    prepopulated_fields = {'slug': ('title',)}

class ServiceListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'service_type', 'service_area', 'vendor', 'status', 'date_posted']
    list_filter = ['status', 'service_type', 'category']
    search_fields = ['title', 'description', 'service_type', 'service_area']
    prepopulated_fields = {'slug': ('title',)}

class PaybillAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'service_category', 'payment_provider', 'vendor', 'status', 'date_posted']
    list_filter = ['status', 'service_category', 'payment_provider', 'category']
    search_fields = ['title', 'description', 'service_category', 'payment_provider']
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(store_models.Category, CategoryAdmin)
admin.site.register(store_models.Product, ProductAdmin)
admin.site.register(store_models.Variant, VariantAdmin)
admin.site.register(store_models.VariantItem, VariantItemAdmin)
admin.site.register(store_models.Gallery, GalleryAdmin)
admin.site.register(store_models.Cart, CartAdmin)
admin.site.register(store_models.Coupon, CouponAdmin)
admin.site.register(store_models.Order, OrderAdmin)
admin.site.register(store_models.OrderItem, OrderItemAdmin)
admin.site.register(store_models.Review, ReviewAdmin)

# Register specialized listing models
try:
    admin.site.register(store_models.RealEstateListing, RealEstateListingAdmin)
    admin.site.register(store_models.VehicleListing, VehicleListingAdmin)
    admin.site.register(store_models.JobListing, JobListingAdmin)
    admin.site.register(store_models.ServiceListing, ServiceListingAdmin)
    admin.site.register(store_models.Paybill, PaybillAdmin)
except admin.sites.AlreadyRegistered:
    pass  # Models already registered
except AttributeError:
    pass  # Models not defined yet
