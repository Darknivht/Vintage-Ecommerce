def user_role_context(request):
    """
    Determine user type with multiple fallback methods for robust detection
    """
    user_type = None
    comparison_count = 0
    
    if request.user.is_authenticated:
        try:
            # Method 1: Check profile.user_type (primary method)
            if hasattr(request.user, 'profile') and request.user.profile.user_type:
                user_type = request.user.profile.user_type
        except:
            pass
        
        # Method 2: Check if user has a vendor relationship (fallback)
        if not user_type:
            try:
                if hasattr(request.user, 'vendor'):
                    user_type = "Vendor"
                else:
                    user_type = "Customer"
            except:
                user_type = "Customer"  # Default fallback
        
        # Get comparison count
        try:
            from store.models import ProductComparison
            comparison = ProductComparison.objects.get(user=request.user)
            comparison_count = comparison.products.count()
        except:
            comparison_count = 0
    
    return {
        'user_type': user_type,
        'comparison_count': comparison_count
    }
