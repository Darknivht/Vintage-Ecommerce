from store import models as store_models
from customer import models as customer_models

def default(request):
    # Get categories for navigation
    try:
        category_ = store_models.Category.objects.filter(type="product", parent=None)
    except:
        category_ = []
    
    # Get cart count
    total_cart_items = 0
    try:
        if hasattr(request, 'session') and 'cart_id' in request.session:
            cart_id = request.session['cart_id']
            total_cart_items = store_models.Cart.objects.filter(cart_id=cart_id).count()
        elif request.user.is_authenticated:
            total_cart_items = store_models.Cart.objects.filter(user=request.user).count()
    except:
        total_cart_items = 0

    # Get wishlist count
    wishlist_count = 0
    try:
        if request.user.is_authenticated:
            wishlist_count = customer_models.Wishlist.objects.filter(user=request.user).count()
    except:
        wishlist_count = 0

    # Get user type
    user_type = None
    try:
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            user_type = request.user.profile.user_type
    except:
        user_type = None

    return {
        "total_cart_items": total_cart_items,
        "category_": category_,
        "wishlist_count": wishlist_count,
        "user_type": user_type,
    }