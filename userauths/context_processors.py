def user_role_context(request):
    """
    Determine user type with multiple fallback methods for robust detection
    """
    user_type = None
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
    
    return {'user_type': user_type}
