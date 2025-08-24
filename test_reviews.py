#!/usr/bin/env python
"""
Test script to verify the review system is working correctly
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_prj.settings')
django.setup()

from django.contrib.auth import get_user_model
from store.models import Product, Review
from store.forms import ReviewForm

User = get_user_model()

def test_review_system():
    """Test the review system functionality"""
    print("🧪 Testing Review System...")
    
    # 1. Test Review Model
    print("\n1. Testing Review Model:")
    try:
        # Get first user and product (if they exist)
        user = User.objects.first()
        product = Product.objects.first()
        
        if not user:
            print("❌ No users found. Create a user first.")
            return False
            
        if not product:
            print("❌ No products found. Create a product first.")
            return False
        
        # Create a test review
        review = Review.objects.create(
            user=user,
            product=product,
            rating=5,
            review="This is a test review for the system!",
            active=True
        )
        
        print(f"✅ Successfully created review ID: {review.id}")
        print(f"   User: {review.user.username}")
        print(f"   Product: {review.product.name}")
        print(f"   Rating: {review.rating}/5")
        print(f"   Review: {review.review}")
        
    except Exception as e:
        print(f"❌ Error creating review: {str(e)}")
        return False
    
    # 2. Test Review Form
    print("\n2. Testing Review Form:")
    try:
        form_data = {
            'rating': 4,
            'review': 'Another test review through form validation!'
        }
        
        form = ReviewForm(data=form_data)
        if form.is_valid():
            print("✅ Review form validation passed")
            print(f"   Rating: {form.cleaned_data['rating']}")
            print(f"   Review: {form.cleaned_data['review']}")
        else:
            print(f"❌ Form validation failed: {form.errors}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing form: {str(e)}")
        return False
    
    # 3. Test Product average rating method
    print("\n3. Testing Product average rating calculation:")
    try:
        # Create another review for the same product
        review2 = Review.objects.create(
            user=user,
            product=product,
            rating=3,
            review="Second test review",
            active=True
        )
        
        # Test average rating
        avg_rating = product.average_rating()
        print(f"✅ Average rating calculation works: {avg_rating}")
        
        # Test review count
        review_count = product.reviews.filter(active=True).count()
        print(f"✅ Review count: {review_count}")
        
    except Exception as e:
        print(f"❌ Error testing average rating: {str(e)}")
        return False
    
    # 4. Clean up test data
    print("\n4. Cleaning up test data:")
    try:
        Review.objects.filter(review__contains="test review").delete()
        print("✅ Test reviews cleaned up successfully")
    except Exception as e:
        print(f"❌ Error cleaning up: {str(e)}")
    
    print("\n🎉 Review system test completed successfully!")
    return True

def show_review_urls():
    """Show the available review URLs"""
    print("\n📍 Review System URLs:")
    print("   Submit Review: /product/<slug>/review/")
    print("   View All Reviews: /product/<slug>/reviews/")
    print("   AJAX Submit: /ajax/submit-review/")
    print("   Vendor Reviews: /vendor/reviews/ (for vendors)")

if __name__ == "__main__":
    success = test_review_system()
    show_review_urls()
    
    if success:
        print("\n✨ Review system is ready to use!")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")