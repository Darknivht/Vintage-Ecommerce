#!/usr/bin/env python
"""
Vintage Ecommerce Setup Script
Automates the setup process for the enhanced Vintage ecommerce platform
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_prj.settings')
    django.setup()

def create_sample_data():
    """Create sample data for testing"""
    from store.models import *
    from userauths.models import User
    from django.utils import timezone
    from datetime import timedelta
    
    print("Creating sample data...")
    
    # Create sample brands
    brands_data = [
        {'name': 'Apple', 'description': 'Premium technology products'},
        {'name': 'Samsung', 'description': 'Innovative electronics'},
        {'name': 'Nike', 'description': 'Athletic wear and footwear'},
        {'name': 'Adidas', 'description': 'Sports and lifestyle brand'},
        {'name': 'Sony', 'description': 'Entertainment and electronics'},
    ]
    
    for brand_data in brands_data:
        brand, created = Brand.objects.get_or_create(
            name=brand_data['name'],
            defaults={
                'description': brand_data['description'],
                'is_featured': True
            }
        )
        if created:
            print(f"Created brand: {brand.name}")
    
    # Create sample flash sale
    flash_sale, created = FlashSale.objects.get_or_create(
        name="Weekend Flash Sale",
        defaults={
            'description': 'Amazing deals for the weekend!',
            'start_date': timezone.now(),
            'end_date': timezone.now() + timedelta(days=2),
            'discount_percentage': 25.00,
            'is_active': True
        }
    )
    if created:
        print(f"Created flash sale: {flash_sale.name}")
    
    # Create loyalty program
    loyalty_program, created = LoyaltyProgram.objects.get_or_create(
        name="Vintage Rewards",
        defaults={
            'points_per_dollar': 1.00,
            'min_points_to_redeem': 100,
            'point_value': 0.01,
            'is_active': True
        }
    )
    if created:
        print(f"Created loyalty program: {loyalty_program.name}")
    
    # Create notification types
    notification_types = [
        {'name': 'order_placed', 'description': 'New order placed'},
        {'name': 'order_shipped', 'description': 'Order shipped'},
        {'name': 'order_delivered', 'description': 'Order delivered'},
        {'name': 'flash_sale', 'description': 'Flash sale notification'},
        {'name': 'loyalty_reward', 'description': 'Loyalty points earned'},
    ]
    
    for nt_data in notification_types:
        nt, created = NotificationType.objects.get_or_create(
            name=nt_data['name'],
            defaults={'description': nt_data['description']}
        )
        if created:
            print(f"Created notification type: {nt.name}")
    
    # Create product attributes
    attributes_data = [
        {'name': 'color', 'display_name': 'Color', 'attribute_type': 'select'},
        {'name': 'size', 'display_name': 'Size', 'attribute_type': 'select'},
        {'name': 'material', 'display_name': 'Material', 'attribute_type': 'text'},
        {'name': 'warranty', 'display_name': 'Warranty', 'attribute_type': 'text'},
        {'name': 'brand_model', 'display_name': 'Model', 'attribute_type': 'text'},
    ]
    
    for attr_data in attributes_data:
        attr, created = ProductAttribute.objects.get_or_create(
            name=attr_data['name'],
            defaults={
                'display_name': attr_data['display_name'],
                'attribute_type': attr_data['attribute_type']
            }
        )
        if created:
            print(f"Created product attribute: {attr.display_name}")
    
    print("Sample data creation completed!")

def main():
    """Main setup function"""
    print("🎯 VINTAGE ECOMMERCE SETUP")
    print("=" * 50)
    
    # Setup Django
    setup_django()
    
    # Run migrations
    print("\n1. Running database migrations...")
    try:
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed successfully!")
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return
    
    # Create categories
    print("\n2. Creating categories...")
    try:
        execute_from_command_line(['manage.py', 'create_categories'])
        print("✅ Categories created successfully!")
    except Exception as e:
        print(f"❌ Category creation error: {e}")
    
    # Create sample data
    print("\n3. Creating sample data...")
    try:
        create_sample_data()
        print("✅ Sample data created successfully!")
    except Exception as e:
        print(f"❌ Sample data error: {e}")
    
    # Collect static files
    print("\n4. Collecting static files...")
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Static files collected successfully!")
    except Exception as e:
        print(f"❌ Static files error: {e}")
    
    print("\n🎉 SETUP COMPLETED!")
    print("=" * 50)
    print("Next steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Start the development server: python manage.py runserver")
    print("3. Visit http://127.0.0.1:8000 to see your upgraded Vintage store!")
    print("\n🚀 Your world-class ecommerce platform is ready!")

if __name__ == '__main__':
    main()