from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from store.models import *
from userauths.models import User

# Enhanced Product Views
def enhanced_shop(request):
    """Enhanced shop view with advanced filtering and search"""
    products = Product.objects.filter(status="Published").select_related('category', 'brand', 'vendor')
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query) |
            Q(category__title__icontains=query) |
            Q(brand__name__icontains=query)
        )
    
    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        category = get_object_or_404(Category, id=category_id)
        products = products.filter(category=category)
    
    # Brand filter
    brand_id = request.GET.get('brand')
    if brand_id:
        brand = get_object_or_404(Brand, id=brand_id)
        products = products.filter(brand=brand)
    
    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Rating filter
    min_rating = request.GET.get('min_rating')
    if min_rating:
        products = products.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=min_rating)
    
    # Sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    elif sort_by == 'newest':
        products = products.order_by('-date')
    elif sort_by == 'popular':
        products = products.order_by('-view_count')
    else:
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    # Get filter options
    categories = Category.objects.filter(type='product', parent=None)
    brands = Brand.objects.filter(is_featured=True)
    
    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'query': query,
        'current_category': category_id,
        'current_brand': brand_id,
        'sort_by': sort_by,
    }
    
    return render(request, 'store/enhanced_shop.html', context)

def product_detail_enhanced(request, slug):
    """Enhanced product detail view with recently viewed tracking"""
    product = get_object_or_404(Product, slug=slug, status="Published")
    
    # Track recently viewed for authenticated users
    if request.user.is_authenticated:
        RecentlyViewed.objects.update_or_create(
            user=request.user,
            product=product,
            defaults={'viewed_at': timezone.now()}
        )
    
    # Increment view count
    product.view_count += 1
    product.save(update_fields=['view_count'])
    
    # Get related products
    related_products = Product.objects.filter(
        category=product.category,
        status="Published"
    ).exclude(id=product.id)[:4]
    
    # Get recently viewed products for this user
    recently_viewed = []
    if request.user.is_authenticated:
        recently_viewed = RecentlyViewed.objects.filter(
            user=request.user
        ).exclude(product=product).select_related('product')[:5]
    
    # Check if product is in user's wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = WishlistItem.objects.filter(
            user=request.user,
            product=product
        ).exists()
    
    context = {
        'product': product,
        'related_products': related_products,
        'recently_viewed': recently_viewed,
        'in_wishlist': in_wishlist,
    }
    
    return render(request, 'store/product_detail_enhanced.html', context)

# Flash Sale Views
def flash_sales(request):
    """Display active flash sales"""
    active_sales = FlashSale.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).prefetch_related('items__product')
    
    context = {
        'flash_sales': active_sales,
    }
    
    return render(request, 'store/flash_sales.html', context)

def flash_sale_detail(request, sale_id):
    """Display flash sale detail with products"""
    sale = get_object_or_404(FlashSale, id=sale_id, is_active=True)
    
    if not sale.is_live():
        messages.error(request, "This flash sale is not currently active.")
        return redirect('store:flash_sales')
    
    sale_items = sale.items.select_related('product').filter(
        product__status="Published"
    )
    
    context = {
        'sale': sale,
        'sale_items': sale_items,
    }
    
    return render(request, 'store/flash_sale_detail.html', context)

# Wishlist Views
@login_required
def wishlist(request):
    """Display user's wishlist"""
    wishlist_items = WishlistItem.objects.filter(
        user=request.user
    ).select_related('product').order_by('-added_at')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    
    return render(request, 'store/wishlist.html', context)

@login_required
@require_POST
def add_to_wishlist(request):
    """Add product to wishlist via AJAX"""
    product_id = request.POST.get('product_id')
    
    try:
        product = Product.objects.get(id=product_id, status="Published")
        wishlist_item, created = WishlistItem.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to wishlist',
                'action': 'added'
            })
        else:
            wishlist_item.delete()
            return JsonResponse({
                'success': True,
                'message': f'{product.name} removed from wishlist',
                'action': 'removed'
            })
            
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Product not found'
        })

# Product Comparison Views
@login_required
def product_comparison(request):
    """Display product comparison"""
    comparison = ProductComparison.objects.filter(user=request.user).first()
    
    if not comparison:
        comparison = ProductComparison.objects.create(user=request.user)
    
    products = comparison.products.all()
    
    # Get all attributes for comparison
    attributes = ProductAttribute.objects.all()
    
    context = {
        'comparison': comparison,
        'products': products,
        'attributes': attributes,
    }
    
    return render(request, 'store/product_comparison.html', context)

@login_required
@require_POST
def add_to_comparison(request):
    """Add product to comparison via AJAX"""
    product_id = request.POST.get('product_id')
    
    try:
        product = Product.objects.get(id=product_id, status="Published")
        comparison, created = ProductComparison.objects.get_or_create(
            user=request.user
        )
        
        if comparison.products.count() >= 4:
            return JsonResponse({
                'success': False,
                'message': 'You can only compare up to 4 products'
            })
        
        if product in comparison.products.all():
            comparison.products.remove(product)
            return JsonResponse({
                'success': True,
                'message': f'{product.name} removed from comparison',
                'action': 'removed'
            })
        else:
            comparison.products.add(product)
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to comparison',
                'action': 'added'
            })
            
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Product not found'
        })

# Bundle Views
def bundles(request):
    """Display available bundles"""
    active_bundles = Bundle.objects.filter(is_active=True).prefetch_related('items__product')
    
    context = {
        'bundles': active_bundles,
    }
    
    return render(request, 'store/bundles.html', context)

def bundle_detail(request, bundle_id):
    """Display bundle detail"""
    bundle = get_object_or_404(Bundle, id=bundle_id, is_active=True)
    bundle_items = bundle.items.select_related('product')
    
    context = {
        'bundle': bundle,
        'bundle_items': bundle_items,
    }
    
    return render(request, 'store/bundle_detail.html', context)

# Loyalty Program Views
@login_required
def loyalty_dashboard(request):
    """Display user's loyalty account dashboard"""
    loyalty_account, created = CustomerLoyaltyAccount.objects.get_or_create(
        customer=request.user
    )
    
    recent_transactions = PointTransaction.objects.filter(
        account=loyalty_account
    ).order_by('-created_at')[:10]
    
    context = {
        'loyalty_account': loyalty_account,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'customer/loyalty_dashboard.html', context)

# Advanced Search Views
def advanced_search(request):
    """Advanced search with filters"""
    products = Product.objects.filter(status="Published")
    
    # Apply filters from request
    filters = {}
    
    # Category filter
    if request.GET.get('category'):
        filters['category_id'] = request.GET.get('category')
    
    # Brand filter
    if request.GET.get('brand'):
        filters['brand_id'] = request.GET.get('brand')
    
    # Price range
    if request.GET.get('min_price'):
        filters['price__gte'] = request.GET.get('min_price')
    if request.GET.get('max_price'):
        filters['price__lte'] = request.GET.get('max_price')
    
    # Apply filters
    if filters:
        products = products.filter(**filters)
    
    # Search query
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    # Get filter options
    categories = Category.objects.filter(type='product')
    brands = Brand.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'query': query,
    }
    
    return render(request, 'store/advanced_search.html', context)

# AJAX Views for Enhanced Functionality
@csrf_exempt
def quick_view(request):
    """Quick view product details via AJAX"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        
        try:
            product = Product.objects.get(id=product_id, status="Published")
            
            data = {
                'success': True,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': str(product.price),
                    'regular_price': str(product.regular_price) if product.regular_price else None,
                    'image': product.image.url if product.image else None,
                    'description': product.description,
                    'stock': product.stock,
                    'vendor': product.vendor.username if product.vendor else 'Vintage Store',
                    'category': product.category.title if product.category else '',
                    'brand': product.brand.name if product.brand else '',
                }
            }
            
            return JsonResponse(data)
            
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not found'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@login_required
def notifications(request):
    """Display user notifications"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')
    
    # Mark notifications as read when viewed
    notifications.filter(is_read=False).update(is_read=True)
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'customer/notifications.html', context)

# Vendor Analytics Views (for vendors)
@login_required
def vendor_analytics(request):
    """Vendor analytics dashboard"""
    if not hasattr(request.user, 'vendor_profile'):
        messages.error(request, "You need to be a vendor to access this page.")
        return redirect('store:index')
    
    # Get vendor's products
    products = Product.objects.filter(vendor=request.user)
    
    # Calculate analytics
    total_products = products.count()
    total_views = products.aggregate(total_views=models.Sum('view_count'))['total_views'] or 0
    total_orders = OrderItem.objects.filter(vendor=request.user).count()
    total_revenue = OrderItem.objects.filter(vendor=request.user).aggregate(
        total=models.Sum('total')
    )['total'] or 0
    
    # Top performing products
    top_products = products.annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count')[:5]
    
    context = {
        'total_products': total_products,
        'total_views': total_views,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'top_products': top_products,
    }
    
    return render(request, 'vendor/analytics.html', context)