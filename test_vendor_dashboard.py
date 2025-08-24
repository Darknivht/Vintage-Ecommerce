#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
sys.path.append('c:/Users/Toshiba/Desktop/Vintage-Ecommerce')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_prj.settings')
django.setup()

from userauths.models import User, Profile
from vendor.models import Vendor

def test_vendor_dashboard():
    """Test if vendor dashboard functionality works correctly"""
    
    print("=== Testing Vendor Dashboard Functionality ===\n")
    
    # Test 1: Check if we can access vendor models
    try:
        vendors = Vendor.objects.all()
        print(f"✅ Found {vendors.count()} vendors in the system")
        
        for vendor in vendors[:3]:  # Show first 3 vendors
            print(f"   - {vendor.store_name} (User: {vendor.user.username})")
    except Exception as e:
        print(f"❌ Error accessing vendors: {e}")
    
    # Test 2: Check user profiles and user_type
    try:
        users_with_profiles = User.objects.filter(profile__isnull=False).select_related('profile')
        vendor_profiles = users_with_profiles.filter(profile__user_type='Vendor')
        customer_profiles = users_with_profiles.filter(profile__user_type='Customer')
        
        print(f"✅ Found {vendor_profiles.count()} vendor profiles")
        print(f"✅ Found {customer_profiles.count()} customer profiles")
        
        if vendor_profiles.exists():
            print("   Vendor users:")
            for user in vendor_profiles[:3]:
                print(f"   - {user.username} ({user.email}) - Type: {user.profile.user_type}")
                
    except Exception as e:
        print(f"❌ Error accessing user profiles: {e}")
    
    # Test 3: Check vendor dashboard URL patterns
    try:
        from django.urls import reverse
        dashboard_url = reverse('vendor:dashboard')
        print(f"✅ Vendor dashboard URL: {dashboard_url}")
        
        # Test other vendor URLs
        vendor_urls = ['products', 'orders', 'notis']
        for url_name in vendor_urls:
            try:
                url = reverse(f'vendor:{url_name}')
                print(f"✅ Vendor {url_name} URL: {url}")
            except:
                print(f"❌ Could not resolve vendor:{url_name}")
                
    except Exception as e:
        print(f"❌ Error accessing vendor URLs: {e}")
    
    # Test 4: Check if vendor dashboard logic works
    try:
        # Find a test vendor user
        test_vendor = vendor_profiles.first() if vendor_profiles.exists() else None
        
        if test_vendor:
            print(f"\n=== Testing with user: {test_vendor.username} ===")
            print(f"✅ User has profile: {hasattr(test_vendor, 'profile')}")
            print(f"✅ User type: {test_vendor.profile.user_type if hasattr(test_vendor, 'profile') else 'No profile'}")
            print(f"✅ User has vendor profile: {hasattr(test_vendor, 'vendor')}")
            
            if hasattr(test_vendor, 'vendor'):
                print(f"   Store name: {test_vendor.vendor.store_name}")
        else:
            print("⚠️  No vendor users found for testing")
            
    except Exception as e:
        print(f"❌ Error during vendor logic test: {e}")
    
    print("\n=== Test Summary ===")
    print("If all tests pass, vendor dashboard functionality should work correctly.")
    print("Vendors should be redirected to /vendor/dashboard/ after login.")

if __name__ == '__main__':
    test_vendor_dashboard()