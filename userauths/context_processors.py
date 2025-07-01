def user_role_context(request):
    user_type = None
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        user_type = request.user.profile.user_type
    return {'user_type': user_type}
