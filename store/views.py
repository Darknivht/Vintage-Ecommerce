from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, send_mail
from store.utils.paystack import initialize_paystack_transaction
import json
from django.shortcuts import get_object_or_404
from store.utils.flutterwave import initiate_flutterwave_payment
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from store.forms import ListingForm
from store import forms as store_forms
from store.models import Listing
from store.models import Category
from django.core.paginator import Paginator

import json
from store import models as store_models


from decimal import Decimal
import requests
import stripe
from plugin.service_fee import calculate_service_fee
import razorpay

from plugin.paginate_queryset import paginate_queryset
from store import models as store_models
from customer import models as customer_models
from vendor import models as vendor_models
from userauths import models as userauths_models
from plugin.tax_calculation import tax_calculation
from plugin.exchange_rate import convert_ngn_to_inr, convert_ngn_to_kobo, convert_ngn_to_usd, get_ngn_to_usd_rate
from store.models import Category
from store.email_service import email_service

def get_subcategories(request):
    parent_id = request.GET.get("parent_id")
    category_type = request.GET.get("type", None)  # optional, can be 'product' or 'listing'

    if not parent_id:
        return JsonResponse([], safe=False)

    subcategories = Category.objects.filter(parent_id=parent_id)

    # Optional: filter by type if provided (e.g., only 'product' or 'listing' categories)
    if category_type:
        subcategories = subcategories.filter(type=category_type)

    data = [{"id": sub.id, "title": sub.title} for sub in subcategories]

    return JsonResponse(data, safe=False)



stripe.api_key = settings.STRIPE_SECRET_KEY
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def clear_cart_items(request):
    """
    Clear cart items for both authenticated and anonymous users
    """
    try:
        if request.user.is_authenticated:
            # Clear authenticated user's cart
            store_models.Cart.objects.filter(user=request.user).delete()
            print(f"✅ Cleared cart for authenticated user: {request.user.username}")
        else:
            # Clear anonymous user's cart using session cart_id
            cart_id = request.session.get('cart_id')
            if cart_id:
                deleted_count = store_models.Cart.objects.filter(cart_id=cart_id).delete()[0]
                print(f"✅ Cleared {deleted_count} items from anonymous cart: {cart_id}")
                # Clear the cart_id from session
                if 'cart_id' in request.session:
                    del request.session['cart_id']
            else:
                print("ℹ️ No cart_id found in session")
        
        return True
    except Exception as e:
        print(f"❌ Error clearing cart: {str(e)}")
        return False

def index(request):
    # Featured products
    products = store_models.Product.objects.filter(status="Published", featured=True)[:12]
    
    # All products for fallback
    if not products:
        products = store_models.Product.objects.filter(status="Published")[:12]
    
    # Categories for navigation and display
    categories = store_models.Category.objects.filter(type="product", parent=None)
    category_ = categories  # For template compatibility
    
    # Featured categories
    featured_categories = categories.filter(is_featured=True)[:8]
    
    # Brands
    brands = store_models.Brand.objects.filter(is_featured=True)[:10]
    
    # Flash sales
    flash_sales = store_models.FlashSale.objects.filter(is_active=True)
    
    # Get cart and wishlist counts
    cart_count = 0
    wishlist_count = 0
    
    if request.user.is_authenticated:
        try:
            cart_count = store_models.Cart.objects.filter(user=request.user).count()
        except:
            pass
        
        try:
            wishlist_count = store_models.WishlistItem.objects.filter(user=request.user).count()
        except:
            pass
    else:
        # For anonymous users, use session
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart_count = store_models.Cart.objects.filter(cart_id=cart_id).count()
    
    # User type for navigation - now handled by context processor
    # (Removed duplicate logic that was overriding the context processor)
    
    context = {
        "products": products,
        "categories": categories,
        "category_": category_,
        "featured_categories": featured_categories,
        "brands": brands,
        "flash_sales": flash_sales,
        "total_cart_items": cart_count,
        "wishlist_count": {"count": wishlist_count},
        # "user_type": user_type,  # Now provided by context processor
    }
    return render(request, "store/index.html", context)


def shop(request):
    products_list = store_models.Product.objects.filter(status="Published")
    
    # Categories for navigation and filtering
    categories = store_models.Category.objects.filter(type="product", parent=None)
    category_ = categories  # For template compatibility
    
    # Brands for filtering
    brands = store_models.Brand.objects.all()
    
    # Apply filters
    query = request.GET.get('q')
    category_filter = request.GET.getlist('category')
    brand_filter = request.GET.getlist('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    price_range = request.GET.get('price_range')
    rating_filter = request.GET.get('rating')
    availability_filter = request.GET.getlist('availability')
    sort_by = request.GET.get('sort')
    
    # Enhanced search filter
    if query:
        products_list = products_list.filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(tags__icontains=query) |
            models.Q(category__title__icontains=query) |
            models.Q(brand__name__icontains=query) |
            models.Q(vendor__username__icontains=query)
        ).distinct()
    
    # Category filter
    if category_filter:
        products_list = products_list.filter(category__id__in=category_filter)
    
    # Brand filter
    if brand_filter:
        products_list = products_list.filter(brand__id__in=brand_filter)
    
    # Price filters
    if min_price:
        try:
            products_list = products_list.filter(price__gte=Decimal(min_price))
        except:
            pass
    
    if max_price:
        try:
            products_list = products_list.filter(price__lte=Decimal(max_price))
        except:
            pass
    
    # Price range filter
    if price_range:
        if price_range == '0-10000':
            products_list = products_list.filter(price__lt=10000)
        elif price_range == '10000-50000':
            products_list = products_list.filter(price__gte=10000, price__lt=50000)
        elif price_range == '50000-100000':
            products_list = products_list.filter(price__gte=50000, price__lt=100000)
        elif price_range == '100000-500000':
            products_list = products_list.filter(price__gte=100000, price__lt=500000)
        elif price_range == '500000-':
            products_list = products_list.filter(price__gte=500000)
    
    # Rating filter
    if rating_filter:
        try:
            rating_value = int(rating_filter)
            # This would need a custom annotation for average rating
            # For now, we'll skip this complex filter
        except:
            pass
    
    # Availability filters
    if availability_filter:
        if 'in_stock' in availability_filter:
            products_list = products_list.filter(stock__gt=0)
        if 'on_sale' in availability_filter:
            products_list = products_list.filter(regular_price__gt=models.F('price'))
        if 'featured' in availability_filter:
            products_list = products_list.filter(featured=True)
    
    # Sorting
    if sort_by:
        if sort_by == 'name':
            products_list = products_list.order_by('name')
        elif sort_by == '-name':
            products_list = products_list.order_by('-name')
        elif sort_by == 'price':
            products_list = products_list.order_by('price')
        elif sort_by == '-price':
            products_list = products_list.order_by('-price')
        elif sort_by == '-date':
            products_list = products_list.order_by('-date')
        elif sort_by == 'date':
            products_list = products_list.order_by('date')
        elif sort_by == '-popularity':
            products_list = products_list.order_by('-view_count')
    
    # Variant data for filters
    colors = store_models.VariantItem.objects.filter(variant__name='Color').values('title', 'content').distinct()
    sizes = store_models.VariantItem.objects.filter(variant__name='Size').values('title', 'content').distinct()

    item_display = [
        {"id": "1", "value": 1},
        {"id": "2", "value": 2},
        {"id": "3", "value": 3},
        {"id": "40", "value": 40},
        {"id": "50", "value": 50},
        {"id": "100", "value": 100},
    ]

    ratings = [
        {"id": "1", "value": "★☆☆☆☆"},
        {"id": "2", "value": "★★☆☆☆"},
        {"id": "3", "value": "★★★☆☆"},
        {"id": "4", "value": "★★★★☆"},
        {"id": "5", "value": "★★★★★"},
    ]

    prices = [
        {"id": "lowest", "value": "Highest to Lowest"},
        {"id": "highest", "value": "Lowest to Highest"},
    ]

    # Pagination
    products = paginate_queryset(request, products_list, 12)
    
    # Get cart and wishlist counts
    cart_count = 0
    wishlist_count = 0
    
    if request.user.is_authenticated:
        try:
            cart_count = store_models.Cart.objects.filter(user=request.user).count()
        except:
            pass
        
        try:
            wishlist_count = store_models.WishlistItem.objects.filter(user=request.user).count()
        except:
            pass
    else:
        # For anonymous users, use session
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart_count = store_models.Cart.objects.filter(cart_id=cart_id).count()
    
    # User type for navigation - now handled by context processor
    # (Removed duplicate logic that was overriding the context processor)

    context = {
        "products": products,
        "products_list": products_list,
        "categories": categories,
        "category_": category_,
        "brands": brands,
        "colors": colors,
        "sizes": sizes,
        "item_display": item_display,
        "ratings": ratings,
        "prices": prices,
        "total_cart_items": cart_count,
        "wishlist_count": {"count": wishlist_count},
        # "user_type": user_type,  # Now provided by context processor
    }
    return render(request, "store/shop.html", context)


def category(request, id):
    category = get_object_or_404(store_models.Category, id=id, type="product")

    subcategories = category.subcategories.all()
    categories_to_include = [category] + list(subcategories)

    products_list = store_models.Product.objects.filter(
        status="Published",
        category__in=categories_to_include
    )

    query = request.GET.get("q")
    if query:
        products_list = products_list.filter(name__icontains=query)

    products = paginate_queryset(request, products_list, 10)

    context = {
        "products": products,
        "products_list": products_list,
        "category": category,
    }
    return render(request, "store/category.html", context)



def vendors(request):
    vendors = userauths_models.Profile.objects.filter(user_type="Vendor")
    
    context = {
        "vendors": vendors
    }
    return render(request, "store/vendors.html", context)

def product_detail(request, slug):
    product = store_models.Product.objects.get(status="Published", slug=slug)
    product_stock_range = range(1, product.stock + 1)

    related_products = store_models.Product.objects.filter(category=product.category).exclude(id=product.id)

    context = {
        "product": product,
        "product_stock_range": product_stock_range,
        "related_products": related_products,
    }
    return render(request, "store/product_detail.html", context)

@csrf_exempt
def add_to_cart(request):
    # Handle both GET and POST requests
    if request.method == 'POST':
        try:
            # Try to parse JSON body (from modern AJAX calls)
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                id = data.get('product_id')
                qty = data.get('quantity', 1)
                color = data.get('color', '')
                size = data.get('size', '')
                cart_id = request.session.get('cart_id')
                if not cart_id:
                    import uuid
                    cart_id = str(uuid.uuid4())
                    request.session['cart_id'] = cart_id
            else:
                # Handle form-encoded POST data
                id = request.POST.get("id")
                qty = request.POST.get("qty")
                color = request.POST.get("color")
                size = request.POST.get("size")
                cart_id = request.POST.get("cart_id")
        except:
            # Fallback to GET parameters
            id = request.GET.get("id")
            qty = request.GET.get("qty")
            color = request.GET.get("color")
            size = request.GET.get("size")
            cart_id = request.GET.get("cart_id")
    else:
        # GET request - original behavior
        id = request.GET.get("id")
        qty = request.GET.get("qty")
        color = request.GET.get("color")
        size = request.GET.get("size")
        cart_id = request.GET.get("cart_id")
    
    # Ensure cart_id is set (generate if needed for anonymous users)
    if not cart_id and not request.user.is_authenticated:
        import uuid
        cart_id = str(uuid.uuid4())
        request.session['cart_id'] = cart_id
    elif cart_id:
        request.session['cart_id'] = cart_id

    # Validate required fields
    if not id or not qty:
        return JsonResponse({"error": "Product ID and quantity are required", "success": False}, status=400)

    # Try to fetch the product, return an error if it doesn't exist
    try:
        product = store_models.Product.objects.get(status="Published", id=id)
    except store_models.Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)

    # Check if the item is already in the cart
    if request.user.is_authenticated:
        existing_cart_item = store_models.Cart.objects.filter(user=request.user, product=product).first()
    else:
        existing_cart_item = store_models.Cart.objects.filter(cart_id=cart_id, product=product).first()

    # Check if quantity that user is adding exceed item stock qty
    if int(qty) > product.stock:
        return JsonResponse({"error": "Qty exceed current stock amount"}, status=404)

    # If the item is not in the cart, create a new cart entry
    if not existing_cart_item:
        cart = store_models.Cart()
        cart.product = product
        cart.qty = qty
        cart.price = product.price
        cart.color = color
        cart.size = size
        cart.sub_total = Decimal(product.price) * Decimal(qty)
        cart.shipping = Decimal(product.shipping) * Decimal(qty)
        cart.total = cart.sub_total + cart.shipping
        cart.user = request.user if request.user.is_authenticated else None
        cart.cart_id = cart_id
        cart.save()

        message = "Item added to cart"
    else:
        # If the item exists in the cart, update the existing entry
        existing_cart_item.color = color
        existing_cart_item.size = size
        existing_cart_item.qty = qty
        existing_cart_item.price = product.price
        existing_cart_item.sub_total = Decimal(product.price) * Decimal(qty)
        existing_cart_item.shipping = Decimal(product.shipping) * Decimal(qty)
        existing_cart_item.total = existing_cart_item.sub_total +  existing_cart_item.shipping
        existing_cart_item.user = request.user if request.user.is_authenticated else None
        existing_cart_item.cart_id = cart_id
        existing_cart_item.save()

        message = "Cart updated"

    # Count the total number of items in the cart
    if request.user.is_authenticated:
        total_cart_items = store_models.Cart.objects.filter(user=request.user)
        cart_sub_total = store_models.Cart.objects.filter(user=request.user).aggregate(sub_total = models.Sum("sub_total"))['sub_total']
    else:
        total_cart_items = store_models.Cart.objects.filter(cart_id=cart_id)
        cart_sub_total = store_models.Cart.objects.filter(cart_id=cart_id).aggregate(sub_total = models.Sum("sub_total"))['sub_total']

    # Return the response with the cart update message and total cart items
    # Support both legacy and modern response formats
    response_data = {
        "message": message,
        "total_cart_items": total_cart_items.count(),
        "cart_sub_total": "{:,.2f}".format(cart_sub_total),
        "item_sub_total": "{:,.2f}".format(existing_cart_item.sub_total) if existing_cart_item else "{:,.2f}".format(cart.sub_total),
        # Modern format compatibility
        "success": True,
        "cart_count": total_cart_items.count()
    }
    return JsonResponse(response_data)

def cart(request):
    # Handle both authenticated and anonymous users
    if request.user.is_authenticated:
        items = store_models.Cart.objects.filter(user=request.user)
        cart_sub_total = store_models.Cart.objects.filter(user=request.user).aggregate(sub_total = models.Sum("sub_total"))['sub_total']
    else:
        if "cart_id" in request.session:
            cart_id = request.session['cart_id']
        else:
            cart_id = None
        
        items = store_models.Cart.objects.filter(cart_id=cart_id)
        cart_sub_total = store_models.Cart.objects.filter(cart_id=cart_id).aggregate(sub_total = models.Sum("sub_total"))['sub_total']
    
    try:
        addresses = customer_models.Address.objects.filter(user=request.user) if request.user.is_authenticated else None
    except:
        addresses = None

    if not items:
        messages.warning(request, "No item in cart")
        return redirect("store:index")

    context = {
        "items": items,
        "cart_sub_total": cart_sub_total,
        "addresses": addresses,
    }
    return render(request, "store/cart.html", context)

def delete_cart_item(request):
    id = request.GET.get("id")
    item_id = request.GET.get("item_id")
    cart_id = request.GET.get("cart_id")
    
    # Validate required fields
    if not id and not item_id and not cart_id:
        return JsonResponse({"error": "Item or Product id not found"}, status=400)

    try:
        product = store_models.Product.objects.get(status="Published", id=id)
    except store_models.Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)

    # Check if the item is already in the cart
    item = store_models.Cart.objects.get(product=product, id=item_id)
    item.delete()

    # Count the total number of items in the cart
    total_cart_items = store_models.Cart.objects.filter(cart_id=cart_id)
    cart_sub_total = store_models.Cart.objects.filter(cart_id=cart_id).aggregate(sub_total = models.Sum("sub_total"))['sub_total']

    return JsonResponse({
        "message": "Item deleted",
        "total_cart_items": total_cart_items.count(),
        "cart_sub_total": "{:,.2f}".format(cart_sub_total) if cart_sub_total else 0.00
    })

def create_order(request):
    if request.method == "POST":
        address_id = request.POST.get("address")
        if not address_id:
            messages.warning(request, "Please select an address to continue")
            return redirect("store:cart")
        
        address = customer_models.Address.objects.filter(user=request.user, id=address_id).first()

        if "cart_id" in request.session:
            cart_id = request.session['cart_id']
        else:
            cart_id = None

        items = store_models.Cart.objects.filter(cart_id=cart_id)
        cart_sub_total = store_models.Cart.objects.filter(cart_id=cart_id).aggregate(sub_total = models.Sum("sub_total"))['sub_total']
        cart_shipping_total = store_models.Cart.objects.filter(cart_id=cart_id).aggregate(shipping = models.Sum("shipping"))['shipping']
        
        order = store_models.Order()
        order.sub_total = cart_sub_total
        order.customer = request.user
        order.address = address
        order.shipping = cart_shipping_total
        order.total = order.sub_total + order.shipping
        order.save()

        for i in items:
            store_models.OrderItem.objects.create(
                order=order,
                product=i.product,
                qty=i.qty,
                color=i.color,
                size=i.size,
                price=i.price,
                sub_total=i.sub_total,
                shipping=i.shipping,
                total=i.total,
                initial_total=i.total,
                vendor=i.product.vendor
            )

            order.vendors.add(i.product.vendor)
        
    
    return redirect("store:checkout", order.order_id)

def coupon_apply(request, order_id):
    print("Order Id ========", order_id)
    
    try:
        order = store_models.Order.objects.get(order_id=order_id)
        order_items = store_models.OrderItem.objects.filter(order=order)
    except store_models.Order.DoesNotExist:
        messages.error(request, "Order not found")
        return redirect("store:cart")

    if request.method == 'POST':
        coupon_code = request.POST.get("coupon_code")
        
        if not coupon_code:
            messages.error(request, "No coupon entered")
            return redirect("store:checkout", order.order_id)
            
        try:
            coupon = store_models.Coupon.objects.get(code=coupon_code)
        except store_models.Coupon.DoesNotExist:
            messages.error(request, "Coupon does not exist")
            return redirect("store:checkout", order.order_id)
        
        if coupon in order.coupons.all():
            messages.warning(request, "Coupon already activated")
            return redirect("store:checkout", order.order_id)
        else:
            # Assuming coupon applies to specific vendor items, not globally
            total_discount = 0
            for item in order_items:
                if coupon.vendor == item.product.vendor and coupon not in item.coupon.all():
                    item_discount = item.total * coupon.discount / 100  # Discount for this item
                    total_discount += item_discount

                    item.coupon.add(coupon) 
                    item.total -= item_discount
                    item.saved += item_discount
                    item.save()

            # Apply total discount to the order after processing all items
            if total_discount > 0:
                order.coupons.add(coupon)
                order.total -= total_discount
                order.sub_total -= total_discount
                order.saved += total_discount
                order.save()
        
        messages.success(request, "Coupon Activated")
        return redirect("store:checkout", order.order_id)


# store/views.py

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.conf import settings

from store import models as store_models
from store.utils.paystack import create_paystack_split_payment

@login_required
def checkout(request, order_id):
    """
    Enhanced marketplace checkout with proper split payment handling
    """
    # Fetch order
    order = get_object_or_404(store_models.Order, order_id=order_id)
    
    # Build callback URL
    callback_url = request.build_absolute_uri(
        reverse("store:paystack_payment_verify", args=[order.order_id])
    ) + "?payment_method=Paystack"
    
    # Create Paystack split payment
    payment_result = create_paystack_split_payment(order, callback_url)
    
    if not payment_result["success"]:
        error_msg = payment_result.get("error", "Failed to initialize payment")
        messages.error(request, f"Payment initialization failed: {error_msg}")
        
        # Show split info for debugging
        split_info = payment_result.get("split_info", {})
        if split_info:
            messages.info(request,
                f"Order has {split_info['vendor_count']} vendor(s), "
                f"{split_info['vendors_with_subaccounts']} with valid subaccounts"
            )
        
        return redirect("store:cart")
    
    # Get split information for display
    split_info = payment_result["split_info"]
    
    context = {
        "order": order,
        "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY,
        "paystack_checkout_link": payment_result["authorization_url"],
        "split_info": split_info,
        "vendor_count": split_info["vendor_count"],
        "vendors_with_subaccounts": split_info["vendors_with_subaccounts"],
        "platform_fee_total": split_info["platform_fee_total"],
    }
    return render(request, "store/checkout.html", context)






@csrf_exempt
def stripe_payment(request, order_id):
    order = store_models.Order.objects.get(order_id=order_id)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    checkout_session = stripe.checkout.Session.create(
        customer_email = order.address.email,
        payment_method_types=['card'],
        line_items = [
            {
                'price_data': {
                    'currency': 'NGN',
                    'product_data': {
                        'name': order.address.full_name
                    },
                    'unit_amount': int(order.total * 100)
                },
                'quantity': 1
            }
        ],
        mode = 'payment',
        success_url = request.build_absolute_uri(reverse("store:stripe_payment_verify", args=[order.order_id])) + "?session_id={CHECKOUT_SESSION_ID}" + "&payment_method=Stripe",
        cancel_url = request.build_absolute_uri(reverse("store:stripe_payment_verify", args=[order.order_id]))
    )

    print("checkkout session", checkout_session)
    return JsonResponse({"sessionId": checkout_session.id})

def stripe_payment_verify(request, order_id):
    order = store_models.Order.objects.get(order_id=order_id)

    session_id = request.GET.get("session_id")
    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status == "paid":
        if order.payment_status == "Processing":
            order.payment_status = "Paid"
            order.save()
            # Clear cart after successful payment
            clear_cart_items(request)
            
            # Create notification for customer
            customer_models.Notifications.objects.create(type="New Order", user=request.user)
            
            # Send order confirmation email to customer
            email_service.send_order_confirmation(order, order.address.email)
            
            # Send new order notifications to vendors
            vendors_notified = set()
            for item in order.order_items():
                if item.vendor and item.vendor.email and item.vendor not in vendors_notified:
                    email_service.send_new_order_to_vendor(order, item.vendor)
                    vendors_notified.add(item.vendor)

            return redirect(f"/payment_status/{order.order_id}/?payment_status=paid")
    
    return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")
    
def get_paypal_access_token():
    token_url = 'https://api.sandbox.paypal.com/v1/oauth2/token'
    data = {'grant_type': 'client_credentials'}
    auth = (settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET_ID)
    response = requests.post(token_url, data=data, auth=auth)

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f'Failed to get access token from PayPal. Status code: {response.status_code}') 

def paypal_payment_verify(request, order_id):
    order = store_models.Order.objects.get(order_id=order_id)

    transaction_id = request.GET.get("transaction_id")
    paypal_api_url = f'https://api-m.sandbox.paypal.com/v2/checkout/orders/{transaction_id}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {get_paypal_access_token()}',
    }
    response = requests.get(paypal_api_url, headers=headers)

    if response.status_code == 200:
        paypal_order_data = response.json()
        paypal_payment_status = paypal_order_data['status']
        if paypal_payment_status == 'COMPLETED':
            if order.payment_status == "Processing":
                order.payment_status = "Paid"
                payment_method = request.GET.get("payment_method")
                order.payment_method = payment_method
                order.save()
                clear_cart_items(request)
                return redirect(f"/payment_status/{order.order_id}/?payment_status=paid")
    else:
        return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")

@csrf_exempt
def razorpay_payment_verify(request, order_id):
    order = store_models.Order.objects.get(order_id=order_id)
    payment_method = request.GET.get("payment_method")

    if request.method == "POST":
        data = request.POST

        # Extract payment data
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        print("razorpay_order_id: ====", razorpay_order_id)
        print("razorpay_payment_id: ====", razorpay_payment_id)
        print("razorpay_signature: ====", razorpay_signature)

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        # Verify the payment signature
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })

        razorpay_client.utility.verify_payment_signature(params_dict)

        # Success response
        if order.payment_status == "Processing":
            order.payment_status = "Paid"
            order.payment_method = payment_method
            order.save()
            
            # Clear cart after successful payment
            clear_cart_items(request)
            
            # Create notifications
            customer_models.Notifications.objects.create(type="New Order", user=request.user)
            for item in order.order_items():
                vendor_models.Notifications.objects.create(type="New Order", user=item.vendor)
            
            # Send order confirmation email to customer
            email_service.send_order_confirmation(order, order.address.email)
            
            # Send new order notifications to vendors
            vendors_notified = set()
            for item in order.order_items():
                if item.vendor and item.vendor.email and item.vendor not in vendors_notified:
                    email_service.send_new_order_to_vendor(order, item.vendor)
                    vendors_notified.add(item.vendor)

            return redirect(f"/payment_status/{order.order_id}/?payment_status=paid")

        

    return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")

def paystack_payment_verify(request, order_id):
    """
    Enhanced payment verification with marketplace split payment support
    """
    from store.utils.paystack import verify_paystack_transaction
    from customer import models as customer_models
    from vendor import models as vendor_models
    from django.template.loader import render_to_string
    from django.core.mail import EmailMultiAlternatives
    
    order = get_object_or_404(store_models.Order, order_id=order_id)
    reference = request.GET.get('reference', '')

    if not reference:
        messages.error(request, "Invalid payment reference.")
        return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")

    # Verify transaction with Paystack
    response_data = verify_paystack_transaction(reference)

    # Check API response
    if not response_data.get('status'):
        error_msg = response_data.get('message', 'Payment verification failed')
        messages.error(request, f"Payment verification failed: {error_msg}")
        return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")

    tx_data = response_data.get("data", {})
    tx_status = tx_data.get("status")
    
    if tx_status == "success":
        if order.payment_status == "Processing":
            # Mark as paid
            order.payment_status = "Paid"
            order.payment_method = request.GET.get("payment_method", "Paystack")
            order.payment_id = reference
            order.save()

            # Update order items
            store_models.OrderItem.objects.filter(order=order).update(order_status="Processing")

            # Clear cart
            clear_cart_items(request)

            # Send notifications
            try:
                # Customer notification
                customer_models.Notifications.objects.create(type="New Order", user=request.user)
                
                # Vendor notifications
                for item in order.order_items():
                    vendor_models.Notifications.objects.create(type="New Order", user=item.vendor)

                # Send order confirmation email to customer
                email_service.send_order_confirmation(order, order.address.email)
                
                # Send new order notifications to vendors
                vendors_notified = set()
                for item in order.order_items():
                    if item.vendor and item.vendor.email and item.vendor not in vendors_notified:
                        email_service.send_new_order_to_vendor(order, item.vendor)
                        vendors_notified.add(item.vendor)
                
            except Exception as e:
                print(f"[Email/Notification Error] {e}")

            messages.success(request, "Payment successful! Your order has been confirmed.")
            return redirect(f"/payment_status/{order.order_id}/?payment_status=paid")
        else:
            messages.warning(request, "Order was already paid.")
            return redirect(f"/payment_status/{order.order_id}/?payment_status=paid")

    # If payment failed
    messages.error(request, f"Payment failed. Status: {tx_status}")
    return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")



def flutterwave_payment_callback(request, order_id):
    order = store_models.Order.objects.get(order_id=order_id)

    payment_id = request.GET.get('tx_ref')
    status = request.GET.get('status')

    headers = {
        'Authorization': f'Bearer {settings.FLUTTERWAVE_PRIVATE_KEY}'
    }
    response = requests.get(f'https://api.flutterwave.com/v3/transactions/{payment_id}/verify', headers=headers)

    if response.status_code == 200:
        if order.payment_status == "Processing":
            order.payment_status = "Paid"
            payment_method = request.GET.get("payment_method")
            order.payment_method = payment_method
            order.save()
            
            # Clear cart after successful payment
            clear_cart_items(request)
            
            # Create notifications
            customer_models.Notifications.objects.create(type="New Order", user=request.user)
            
            # Send order confirmation email to customer
            email_service.send_order_confirmation(order, order.address.email)
            
            # Send new order notifications to vendors
            vendors_notified = set()
            for item in order.order_items():
                if item.vendor and item.vendor.email and item.vendor not in vendors_notified:
                    email_service.send_new_order_to_vendor(order, item.vendor)
                    vendors_notified.add(item.vendor)
            
            return redirect(f"/payment_status/{order.order_id}/?payment_status=paid")
        else:
            return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")
    else:
        return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")

def payment_status(request, order_id):
    order = store_models.Order.objects.get(order_id=order_id)
    payment_status = request.GET.get("payment_status")

    context = {
        "order": order,
        "payment_status": payment_status
    }
    return render(request, "store/payment_status.html", context)

def filter_products(request):
    products = store_models.Product.objects.all()

    # Get filters from the AJAX request
    categories = request.GET.getlist('categories[]')
    rating = request.GET.getlist('rating[]')
    sizes = request.GET.getlist('sizes[]')
    colors = request.GET.getlist('colors[]')
    price_order = request.GET.get('prices')
    search_filter = request.GET.get('searchFilter')
    display = request.GET.get('display')

    print("categories =======", categories)
    print("rating =======", rating)
    print("sizes =======", sizes)
    print("colors =======", colors)
    print("price_order =======", price_order)
    print("search_filter =======", search_filter)
    print("display =======", display)

   
    # Apply category filtering
    if categories:
        products = products.filter(models.Q(category__id__in=categories) | models.Q(category__parent__id__in=categories))


    # Apply rating filtering
    if rating:
        products = products.filter(reviews__rating__in=rating).distinct()

    

    # Apply size filtering
    if sizes:
        products = products.filter(variant__variant_items__content__in=sizes).distinct()

    # Apply color filtering
    if colors:
        products = products.filter(variant__variant_items__content__in=colors).distinct()

    # Apply price ordering
    if price_order == 'lowest':
        products = products.order_by('-price')
    elif price_order == 'highest':
        products = products.order_by('price')

    # Apply search filter
    if search_filter:
        products = products.filter(name__icontains=search_filter)

    if display:
        products = products.filter()[:int(display)]


    # Render the filtered products as HTML using render_to_string
    html = render_to_string('partials/_store.html', {'products': products})

    return JsonResponse({'html': html, 'product_count': products.count()})

def order_tracker_page(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        return redirect("store:order_tracker_detail", item_id)
    
    return render(request, "store/order_tracker_page.html")

def order_tracker_detail(request, item_id):
    try:
        item = store_models.OrderItem.objects.filter(models.Q(item_id=item_id) | models.Q(tracking_id=item_id)).first()
    except:
        item = None
        messages.error(request, "Order not found!")
        return redirect("store:order_tracker_page")
    
    context = {
        "item": item,
    }
    return render(request, "store/order_tracker.html", context)

def about(request):
    return render(request, "pages/about.html")

def contact(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        userauths_models.ContactMessage.objects.create(
            full_name=full_name,
            email=email,
            subject=subject,
            message=message,
        )
        messages.success(request, "Message sent successfully")
        return redirect("store:contact")
    return render(request, "pages/contact.html")

def faqs(request):
    return render(request, "pages/faqs.html")

def privacy_policy(request):
    return render(request, "pages/privacy_policy.html")

def terms_conditions(request):
    return render(request, "pages/terms_conditions.html")


@login_required
def create_listing(request):
    from store.forms import ListingForm
    
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.vendor = request.user
            listing.save()
            
            # Handle additional gallery images if provided
            gallery_data = form.cleaned_data.get('gallery_images')
            if gallery_data and isinstance(gallery_data, str):
                try:
                    import json
                    gallery_list = json.loads(gallery_data)
                    from store.models import ListingImage
                    for i, image_url in enumerate(gallery_list):
                        ListingImage.objects.create(
                            listing=listing,
                            image=image_url,
                            order=i
                        )
                except json.JSONDecodeError:
                    pass
            
            messages.success(request, f"Listing '{listing.title}' created successfully!")
            return redirect("store:vendor_listings")
        else:
            messages.error(request, "Please correct the errors below.")
            print("🚨 Form errors:", form.errors)
    else:
        form = ListingForm()

    categories = Category.objects.filter(type="listing", parent=None)
    
    return render(request, "vendor/create_listing.html", {
        "form": form,
        "categories": categories,
        "page_title": "Create New Listing"
    })


@login_required  
def edit_listing(request, listing_id):
    from store.forms import ListingForm
    
    listing = get_object_or_404(Listing, id=listing_id, vendor=request.user)
    
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, f"Listing '{listing.title}' updated successfully!")
            return redirect("store:vendor_listings")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ListingForm(instance=listing)

    categories = Category.objects.filter(type="listing", parent=None)
    
    return render(request, "vendor/edit_listing.html", {
        "form": form,
        "listing": listing,
        "categories": categories,
        "page_title": f"Edit {listing.title}"
    })


@login_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, vendor=request.user)
    
    if request.method == "POST":
        listing_title = listing.title
        listing.delete()
        messages.success(request, f"Listing '{listing_title}' deleted successfully!")
        return redirect("store:vendor_listings")
    
    return render(request, "vendor/delete_listing_confirm.html", {
        "listing": listing,
        "page_title": f"Delete {listing.title}"
    })


@login_required
def toggle_listing_status(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, vendor=request.user)
    
    if request.method == "POST":
        new_status = request.POST.get('status')
        if new_status in ['published', 'draft', 'expired', 'suspended']:
            listing.status = new_status
            listing.is_active = new_status == 'published'
            listing.save()
            messages.success(request, f"Listing status updated to {new_status.title()}!")
        else:
            messages.error(request, "Invalid status!")
    
    return redirect("store:vendor_listings")




def browse_listings(request):
    from django.db.models import Q
    from store.forms import ListingFilterForm
    
    # Initialize filters
    filter_form = ListingFilterForm(request.GET)
    listings = Listing.objects.filter(status='published', is_active=True)
    
    # Apply filters
    if filter_form.is_valid():
        cleaned_data = filter_form.cleaned_data
        
        # Search filter
        if cleaned_data.get('search'):
            search_query = cleaned_data['search']
            listings = listings.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(tags__icontains=search_query)
            )
        
        # Category filter
        if cleaned_data.get('category'):
            listings = listings.filter(
                Q(category=cleaned_data['category']) |
                Q(subcategory__parent=cleaned_data['category'])
            )
        
        # Listing type filter
        if cleaned_data.get('listing_type'):
            listings = listings.filter(listing_type=cleaned_data['listing_type'])
        
        # Price range filter
        if cleaned_data.get('price_min'):
            listings = listings.filter(price__gte=cleaned_data['price_min'])
        if cleaned_data.get('price_max'):
            listings = listings.filter(price__lte=cleaned_data['price_max'])
        
        # Location filter
        if cleaned_data.get('location'):
            listings = listings.filter(
                Q(location__icontains=cleaned_data['location']) |
                Q(address__icontains=cleaned_data['location'])
            )
        
        # Sort listings
        sort_by = cleaned_data.get('sort_by', '-created_at')
        listings = listings.order_by(sort_by)
    else:
        listings = listings.order_by('-created_at')

    # Pagination
    paginator = Paginator(listings, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get categories and statistics
    categories = Category.objects.filter(type="listing", parent=None)
    featured_listings = Listing.objects.filter(
        status='published', is_active=True, featured=True
    )[:6]
    
    context = {
        "listings": page_obj,
        "filter_form": filter_form,
        "categories": categories,
        "featured_listings": featured_listings,
        "total_listings": listings.count(),
        "page_title": "Browse Listings"
    }

    return render(request, "store/browse_listings.html", context)


def listing_detail(request, slug):
    listing = get_object_or_404(Listing, slug=slug, status='published', is_active=True)
    from store.forms import ListingInquiryForm
    
    # Increment view count
    listing.increment_views()
    
    # Handle inquiry form submission
    inquiry_form = ListingInquiryForm()
    if request.method == 'POST' and 'submit_inquiry' in request.POST:
        inquiry_form = ListingInquiryForm(request.POST)
        if inquiry_form.is_valid():
            from store.models import ListingInquiry
            inquiry = ListingInquiry.objects.create(
                listing=listing,
                inquirer_name=inquiry_form.cleaned_data['name'],
                inquirer_email=inquiry_form.cleaned_data['email'],
                inquirer_phone=inquiry_form.cleaned_data.get('phone', ''),
                message=inquiry_form.cleaned_data['message']
            )
            
            # Update contact count
            listing.contact_count += 1
            listing.save(update_fields=['contact_count'])
            
            messages.success(request, "Your inquiry has been sent successfully! The vendor will contact you soon.")
            return redirect('store:listing_detail', slug=listing.slug)
        else:
            messages.error(request, "Please correct the errors in your inquiry.")
    
    # Get related listings
    related_listings = Listing.objects.filter(
        category=listing.category,
        status='published',
        is_active=True
    ).exclude(id=listing.id)[:4]
    
    # Check if user has favorited this listing
    is_favorited = False
    if request.user.is_authenticated:
        from store.models import ListingFavorite
        is_favorited = ListingFavorite.objects.filter(
            user=request.user, 
            listing=listing
        ).exists()
    
    context = {
        'listing': listing,
        'inquiry_form': inquiry_form,
        'related_listings': related_listings,
        'is_favorited': is_favorited,
        'page_title': listing.title,
        'meta_description': listing.short_description or listing.meta_description
    }
    
    return render(request, 'store/listing_detail.html', context)


@login_required
def vendor_listings(request):
    from django.db.models import Count, Sum, Q
    from store.forms import VendorListingFilterForm
    
    # Initialize filter form
    filter_form = VendorListingFilterForm(request.GET)
    
    # Get base listings queryset
    listings = Listing.objects.filter(vendor=request.user).annotate(
        inquiry_count=Count('inquiries'),
        favorite_count=Count('favorites')
    )
    
    # Apply filters
    if filter_form.is_valid():
        cleaned_data = filter_form.cleaned_data
        
        # Status filter
        status = cleaned_data.get('status', 'all')
        if status != 'all':
            listings = listings.filter(status=status)
        
        # Category filter
        if cleaned_data.get('category'):
            listings = listings.filter(category=cleaned_data['category'])
        
        # Search filter
        if cleaned_data.get('search'):
            search_query = cleaned_data['search']
            listings = listings.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(tags__icontains=search_query)
            )
        
        # Sort listings
        sort_by = cleaned_data.get('sort_by', '-created_at')
        listings = listings.order_by(sort_by)
    else:
        listings = listings.order_by('-created_at')
    
    # Get summary statistics
    all_listings = Listing.objects.filter(vendor=request.user)
    stats = all_listings.aggregate(
        total_listings=Count('id'),
        published_count=Count('id', filter=Q(status='published')),
        draft_count=Count('id', filter=Q(status='draft')),
        sold_count=Count('id', filter=Q(status='sold')),
        total_views=Sum('views_count') or 0,
        total_contacts=Sum('contact_count') or 0,
        total_favorites=Sum('favorites_count') or 0
    )
    
    # Pagination
    paginator = Paginator(listings, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'listings': page_obj,
        'filter_form': filter_form,
        'total_listings': stats['total_listings'],
        'published_count': stats['published_count'],
        'draft_count': stats['draft_count'],
        'sold_count': stats['sold_count'],
        'total_views': stats['total_views'],
        'total_contacts': stats['total_contacts'],
        'total_favorites': stats['total_favorites'],
        'page_title': 'My Listings'
    }
    
    return render(request, 'vendor/vendor_listings.html', context)


# ===== LISTING AJAX VIEWS =====

@csrf_exempt
@login_required
def toggle_listing_favorite(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            listing_id = data.get('listing_id')
            
            listing = get_object_or_404(Listing, id=listing_id, status='published', is_active=True)
            from store.models import ListingFavorite
            
            favorite, created = ListingFavorite.objects.get_or_create(
                user=request.user,
                listing=listing
            )
            
            if not created:
                favorite.delete()
                is_favorited = False
                message = "Removed from favorites"
            else:
                is_favorited = True
                message = "Added to favorites"
                
                # Update favorites count
                listing.favorites_count = listing.favorites.count()
                listing.save(update_fields=['favorites_count'])
            
            return JsonResponse({
                'success': True,
                'is_favorited': is_favorited,
                'message': message,
                'favorites_count': listing.favorites.count()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@csrf_exempt
def get_subcategories(request):
    """AJAX endpoint to get subcategories for a given category"""
    if request.method == 'GET':
        category_id = request.GET.get('category_id')
        
        if category_id:
            try:
                subcategories = Category.objects.filter(
                    parent_id=category_id,
                    type="listing"
                ).values('id', 'title')
                
                return JsonResponse({
                    'success': True,
                    'subcategories': list(subcategories)
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
        
        return JsonResponse({
            'success': True,
            'subcategories': []
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def listing_inquiries(request):
    """View vendor's listing inquiries"""
    from store.models import ListingInquiry
    
    inquiries = ListingInquiry.objects.filter(
        listing__vendor=request.user
    ).select_related('listing').order_by('-created_at')
    
    # Filter by listing if requested
    listing_id = request.GET.get('listing')
    if listing_id:
        inquiries = inquiries.filter(listing_id=listing_id)
    
    # Filter by read status
    read_filter = request.GET.get('read')
    if read_filter == 'unread':
        inquiries = inquiries.filter(is_read=False)
    elif read_filter == 'read':
        inquiries = inquiries.filter(is_read=True)
    
    # Pagination
    paginator = Paginator(inquiries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get vendor's listings for filter dropdown
    vendor_listings = Listing.objects.filter(
        vendor=request.user
    ).values('id', 'title')
    
    context = {
        'inquiries': page_obj,
        'vendor_listings': vendor_listings,
        'selected_listing': int(listing_id) if listing_id else None,
        'read_filter': read_filter or 'all',
        'page_title': 'Listing Inquiries'
    }
    
    return render(request, 'vendor/listing_inquiries.html', context)


@login_required
def mark_inquiry_read(request, inquiry_id):
    """Mark an inquiry as read"""
    from store.models import ListingInquiry
    
    inquiry = get_object_or_404(
        ListingInquiry,
        id=inquiry_id,
        listing__vendor=request.user
    )
    
    inquiry.is_read = True
    inquiry.save(update_fields=['is_read'])
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Inquiry marked as read.')
    return redirect('store:listing_inquiries')


# ===== MODERN AJAX VIEWS =====

@csrf_exempt
def add_to_cart_ajax(request):
    """Modern AJAX add to cart functionality"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))
            
            product = get_object_or_404(store_models.Product, id=product_id, status="Published")
            
            # Check stock
            if product.stock < quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Only {product.stock} items available in stock'
                })
            
            # Get or create cart
            if request.user.is_authenticated:
                cart_item, created = store_models.Cart.objects.get_or_create(
                    user=request.user,
                    product=product,
                    defaults={
                        'qty': quantity,
                        'price': product.price,
                        'sub_total': product.price * quantity,
                        'shipping': product.shipping * quantity,
                        'total': (product.price * quantity) + (product.shipping * quantity)
                    }
                )
                if not created:
                    cart_item.qty += quantity
                    cart_item.sub_total = cart_item.price * cart_item.qty
                    cart_item.shipping = product.shipping * cart_item.qty
                    cart_item.total = cart_item.sub_total + cart_item.shipping
                    cart_item.save()
                
                cart_count = store_models.Cart.objects.filter(user=request.user).count()
            else:
                # Handle anonymous users
                cart_id = request.session.get('cart_id')
                if not cart_id:
                    import uuid
                    cart_id = str(uuid.uuid4())
                    request.session['cart_id'] = cart_id
                
                cart_item, created = store_models.Cart.objects.get_or_create(
                    cart_id=cart_id,
                    product=product,
                    defaults={
                        'qty': quantity,
                        'price': product.price,
                        'sub_total': product.price * quantity,
                        'shipping': product.shipping * quantity,
                        'total': (product.price * quantity) + (product.shipping * quantity)
                    }
                )
                if not created:
                    cart_item.qty += quantity
                    cart_item.sub_total = cart_item.price * cart_item.qty
                    cart_item.shipping = product.shipping * cart_item.qty
                    cart_item.total = cart_item.sub_total + cart_item.shipping
                    cart_item.save()
                
                cart_count = store_models.Cart.objects.filter(cart_id=cart_id).count()
            
            return JsonResponse({
                'success': True,
                'message': 'Product added to cart successfully!',
                'cart_count': cart_count
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@csrf_exempt
def update_cart_ajax(request):
    """Update cart item quantity via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))
            
            if request.user.is_authenticated:
                cart_item = get_object_or_404(store_models.Cart, user=request.user, product_id=product_id)
            else:
                cart_id = request.session.get('cart_id')
                cart_item = get_object_or_404(store_models.Cart, cart_id=cart_id, product_id=product_id)
            
            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.qty = quantity
                cart_item.sub_total = cart_item.price * quantity
                cart_item.shipping = cart_item.product.shipping * quantity
                cart_item.total = cart_item.sub_total + cart_item.shipping
                cart_item.save()
            
            # Calculate totals
            if request.user.is_authenticated:
                cart_items = store_models.Cart.objects.filter(user=request.user)
            else:
                cart_id = request.session.get('cart_id')
                cart_items = store_models.Cart.objects.filter(cart_id=cart_id)
            
            subtotal = sum(item.product.price * item.quantity for item in cart_items)
            total = subtotal  # Add tax/shipping calculation here if needed
            
            return JsonResponse({
                'success': True,
                'subtotal': f'₦{subtotal:,.2f}',
                'total': f'₦{total:,.2f}'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
@csrf_exempt
def toggle_wishlist_ajax(request):
    """Toggle product in wishlist via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            
            product = get_object_or_404(store_models.Product, id=product_id)
            
            wishlist_item, created = store_models.WishlistItem.objects.get_or_create(
                user=request.user,
                product=product
            )
            
            if created:
                added = True
                message = 'Product added to wishlist!'
            else:
                wishlist_item.delete()
                added = False
                message = 'Product removed from wishlist!'
            
            wishlist_count = store_models.WishlistItem.objects.filter(user=request.user).count()
            
            return JsonResponse({
                'success': True,
                'added': added,
                'message': message,
                'wishlist_count': wishlist_count
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def product_quick_view(request, product_id):
    """Enhanced quick view product details via AJAX"""
    try:
        product = get_object_or_404(store_models.Product, id=product_id, status="Published")
        
        # Get related products
        related_products = store_models.Product.objects.filter(
            category=product.category,
            status="Published"
        ).exclude(id=product.id)[:4]
        
        # Get product variants if available
        variants = {}
        for variant in product.variants():
            if variant.is_active:
                variant_items = variant.items()
                if variant_items.exists():
                    variants[variant.name] = []
                    for item in variant_items:
                        variants[variant.name].append({
                            'title': item.title,
                            'content': item.content
                        })
        
        # Check if product is in user's wishlist
        in_wishlist = False
        if request.user.is_authenticated:
            in_wishlist = store_models.WishlistItem.objects.filter(
                user=request.user, 
                product=product
            ).exists()
        
        # Check if product is in comparison
        in_comparison = False
        if request.user.is_authenticated:
            try:
                comparison = store_models.ProductComparison.objects.get(user=request.user)
                in_comparison = product in comparison.products.all()
            except:
                pass
        
        # Render product quick view template
        html = render_to_string('store/partials/product_quick_view.html', {
            'product': product,
            'related_products': related_products,
            'variants': variants,
            'in_wishlist': in_wishlist,
            'in_comparison': in_comparison,
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': html,
            'product_data': {
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'stock': product.stock,
                'in_wishlist': in_wishlist,
                'in_comparison': in_comparison,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


# Product Comparison Views
@csrf_exempt
def toggle_comparison(request):
    """Add/Remove product from comparison list"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Please login to use comparison feature'
        })
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    try:
        product_id = request.POST.get('product_id')
        product = get_object_or_404(store_models.Product, id=product_id, status="Published")
        
        comparison, created = store_models.ProductComparison.objects.get_or_create(
            user=request.user
        )
        
        if product in comparison.products.all():
            comparison.products.remove(product)
            action = 'removed'
            message = f'{product.name} removed from comparison'
        else:
            if comparison.products.count() >= 4:
                return JsonResponse({
                    'success': False,
                    'message': 'You can only compare up to 4 products at once'
                })
            
            comparison.products.add(product)
            action = 'added'
            message = f'{product.name} added to comparison'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'action': action,
            'comparison_count': comparison.products.count()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

def comparison_view(request):
    """View products in comparison"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Please login to use comparison feature')
        return redirect('userauths:sign-in')
    
    try:
        comparison = store_models.ProductComparison.objects.get(user=request.user)
        products = comparison.products.all()
    except:
        products = []
    
    context = {
        'products': products,
        'comparison_count': len(products)
    }
    return render(request, 'store/comparison.html', context)

@csrf_exempt
def clear_comparison(request):
    """Clear all products from comparison"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Please login first'
        })
    
    try:
        comparison = store_models.ProductComparison.objects.get(user=request.user)
        comparison.products.clear()
        return JsonResponse({
            'success': True,
            'message': 'Comparison cleared successfully'
        })
    except:
        return JsonResponse({
            'success': False,
            'message': 'No comparison found'
        })

def search_suggestions(request):
    """Get search suggestions via AJAX"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Get product suggestions
    products = store_models.Product.objects.filter(
        status="Published",
        name__icontains=query
    )[:5]
    
    # Get category suggestions
    categories = store_models.Category.objects.filter(
        title__icontains=query
    )[:3]
    
    suggestions = []
    
    # Add product suggestions
    for product in products:
        suggestions.append({
            'type': 'product',
            'title': product.name,
            'url': f'/product/{product.slug}/',
            'image': product.image.url if product.image else None,
            'price': f'₦{product.price:,.2f}'
        })
    
    # Add category suggestions
    for category in categories:
        suggestions.append({
            'type': 'category',
            'title': category.title,
            'url': f'/category/{category.id}/',
            'count': category.products.count()
        })
    
    return JsonResponse({'suggestions': suggestions})


# ===== BRAND VIEWS =====

def brands_list(request):
    """List all brands"""
    brands = store_models.Brand.objects.all().order_by('name')
    
    context = {
        'brands': brands,
        'categories': store_models.Category.objects.filter(type="product", parent=None),
        'category_': store_models.Category.objects.filter(type="product", parent=None),
    }
    return render(request, 'store/brands.html', context)


def brand_products(request, slug):
    """Show products from a specific brand"""
    brand = get_object_or_404(store_models.Brand, slug=slug)
    products_list = store_models.Product.objects.filter(brand=brand, status="Published")
    
    # Apply search filter
    query = request.GET.get('q')
    if query:
        products_list = products_list.filter(name__icontains=query)
    
    products = paginate_queryset(request, products_list, 12)
    
    context = {
        'brand': brand,
        'products': products,
        'categories': store_models.Category.objects.filter(type="product", parent=None),
        'category_': store_models.Category.objects.filter(type="product", parent=None),
    }
    return render(request, 'store/brand_products.html', context)


# ===== FLASH SALE VIEWS =====

def flash_sales(request):
    """List all active flash sales"""
    flash_sales = store_models.FlashSale.objects.filter(is_active=True)
    
    context = {
        'flash_sales': flash_sales,
        'categories': store_models.Category.objects.filter(type="product", parent=None),
        'category_': store_models.Category.objects.filter(type="product", parent=None),
    }
    return render(request, 'store/flash_sales.html', context)


def flash_sale_detail(request, id):
    """Show flash sale details and products"""
    flash_sale = get_object_or_404(store_models.FlashSale, id=id, is_active=True)
    
    if not flash_sale.is_live():
        messages.warning(request, 'This flash sale is not currently active.')
        return redirect('store:flash_sales')
    
    flash_sale_items = flash_sale.items.all()
    
    context = {
        'flash_sale': flash_sale,
        'flash_sale_items': flash_sale_items,
        'categories': store_models.Category.objects.filter(type="product", parent=None),
        'category_': store_models.Category.objects.filter(type="product", parent=None),
    }
    return render(request, 'store/flash_sale_detail.html', context)


# ===== UTILITY VIEWS =====

def about(request):
    """About page"""
    context = {
        'categories': store_models.Category.objects.filter(type="product", parent=None),
        'category_': store_models.Category.objects.filter(type="product", parent=None),
    }
    return render(request, 'store/about.html', context)


def contact(request):
    """Contact page"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Send email (implement your email logic here)
        try:
            send_mail(
                f'Contact Form: {subject}',
                f'From: {name} ({email})\n\n{message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
        except:
            messages.error(request, 'There was an error sending your message. Please try again.')
        
        return redirect('store:contact')
    
    context = {
        'categories': store_models.Category.objects.filter(type="product", parent=None),
        'category_': store_models.Category.objects.filter(type="product", parent=None),
    }
    return render(request, 'store/contact.html', context)


def faqs(request):
    """FAQs page"""
    context = {
        'categories': store_models.Category.objects.filter(type="product", parent=None),
        'category_': store_models.Category.objects.filter(type="product", parent=None),
    }
    return render(request, 'store/faqs.html', context)


def terms_conditions(request):
    """Terms and Conditions page"""
    context = {
        'categories': store_models.Category.objects.filter(type="product", parent=None),
        'category_': store_models.Category.objects.filter(type="product", parent=None),
    }
    return render(request, 'store/terms_conditions.html', context)


def privacy_policy(request):
    """Privacy Policy page"""
    context = {
        'categories': store_models.Category.objects.filter(type="product", parent=None),
        'category_': store_models.Category.objects.filter(type="product", parent=None),
    }
    return render(request, 'store/privacy_policy.html', context)


# ===== DASHBOARD ROUTING =====

@login_required
def dashboard_redirect(request):
    """Route users to appropriate dashboard based on their user_type"""
    try:
        profile = request.user.profile
        if profile.user_type == 'Vendor':
            return redirect('vendor:dashboard')
        else:
            return redirect('customer:dashboard')
    except:
        # If no profile exists, default to customer dashboard
        return redirect('customer:dashboard')


# ===== REVIEW SYSTEM =====

@login_required
def submit_review(request, product_slug):
    """Submit a review for a product"""
    product = get_object_or_404(store_models.Product, slug=product_slug)
    
    # Check if user has already reviewed this product
    existing_review = store_models.Review.objects.filter(
        user=request.user, 
        product=product
    ).first()
    
    if existing_review:
        messages.warning(request, "You have already reviewed this product.")
        return redirect('store:product_detail', product_slug=product.slug)
    
    # Check if user has purchased this product
    has_purchased = store_models.OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__payment_status="Paid"
    ).exists()
    
    if not has_purchased:
        messages.error(request, "You can only review products you have purchased.")
        return redirect('store:product_detail', product_slug=product.slug)
    
    if request.method == 'POST':
        form = store_forms.ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.active = True  # Auto-approve for now
            review.save()
            
            messages.success(request, "Thank you! Your review has been submitted.")
            return redirect('store:product_detail', product_slug=product.slug)
    else:
        form = store_forms.ReviewForm()
    
    context = {
        'form': form,
        'product': product
    }
    return render(request, 'store/submit_review.html', context)


@require_http_methods(["POST"])
def ajax_submit_review(request):
    """AJAX endpoint for submitting reviews"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False, 
            'message': 'You must be logged in to submit a review.'
        })
    
    try:
        product_id = request.POST.get('product_id')
        product = get_object_or_404(store_models.Product, id=product_id)
        
        # Check if user has already reviewed
        existing_review = store_models.Review.objects.filter(
            user=request.user, 
            product=product
        ).first()
        
        if existing_review:
            return JsonResponse({
                'success': False, 
                'message': 'You have already reviewed this product.'
            })
        
        # Check if user has purchased this product
        has_purchased = store_models.OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__payment_status="Paid"
        ).exists()
        
        if not has_purchased:
            return JsonResponse({
                'success': False, 
                'message': 'You can only review products you have purchased.'
            })
        
        form = store_forms.ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.active = True
            review.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Thank you! Your review has been submitted.',
                'review_count': product.reviews.filter(active=True).count(),
                'average_rating': product.average_rating() or 0
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors in your review.',
                'errors': form.errors
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again.'
        })


def product_reviews(request, product_slug):
    """Display all reviews for a product"""
    product = get_object_or_404(store_models.Product, slug=product_slug)
    reviews = store_models.Review.objects.filter(
        product=product, 
        active=True
    ).select_related('user__profile').order_by('-date')
    
    # Pagination
    paginator = Paginator(reviews, 10)  # Show 10 reviews per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate rating distribution
    rating_distribution = {}
    total_reviews = reviews.count()
    for i in range(1, 6):
        count = reviews.filter(rating=i).count()
        percentage = (count / total_reviews * 100) if total_reviews > 0 else 0
        rating_distribution[i] = {
            'count': count,
            'percentage': percentage
        }
    
    context = {
        'product': product,
        'reviews': page_obj,
        'rating_distribution': rating_distribution,
        'total_reviews': total_reviews,
        'average_rating': product.average_rating() or 0
    }
    return render(request, 'store/product_reviews.html', context)


