"""
Management command to set up comprehensive sample data for Vintage Ecommerce
Creates brands, flash sales, loyalty programs, and sample products
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from store.models import *
from userauths.models import User


class Command(BaseCommand):
    help = 'Set up comprehensive sample data for Vintage Ecommerce'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all data before creating new sample data',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting existing data...')
            self.reset_data()

        self.stdout.write('Creating sample data...')
        
        # Create brands
        self.create_brands()
        
        # Create flash sales
        self.create_flash_sales()
        
        # Create loyalty program
        self.create_loyalty_program()
        
        # Create notification types
        self.create_notification_types()
        
        # Create product attributes
        self.create_product_attributes()
        
        # Create sample vendors
        self.create_sample_vendors()
        
        # Create sample products
        self.create_sample_products()
        
        # Create sample bundles
        self.create_sample_bundles()
        
        # Create sample customer segments
        self.create_customer_segments()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )

    def reset_data(self):
        """Reset existing data"""
        models_to_reset = [
            Brand, FlashSale, FlashSaleItem, Bundle, BundleItem,
            LoyaltyProgram, CustomerLoyaltyAccount, PointTransaction,
            NotificationType, ProductAttribute, ProductAttributeValue,
            CustomerSegment, CustomerProfile
        ]
        
        for model in models_to_reset:
            try:
                model.objects.all().delete()
                self.stdout.write(f'Cleared {model.__name__}')
            except Exception as e:
                self.stdout.write(f'Error clearing {model.__name__}: {e}')

    def create_brands(self):
        """Create sample brands"""
        brands_data = [
            {
                'name': 'Apple',
                'slug': 'apple',
                'description': 'Premium technology products and innovative devices',
                'is_featured': True
            },
            {
                'name': 'Samsung',
                'slug': 'samsung',
                'description': 'Leading electronics and mobile technology',
                'is_featured': True
            },
            {
                'name': 'Nike',
                'slug': 'nike',
                'description': 'Athletic wear, footwear, and sports equipment',
                'is_featured': True
            },
            {
                'name': 'Adidas',
                'slug': 'adidas',
                'description': 'Sports and lifestyle brand',
                'is_featured': True
            },
            {
                'name': 'Sony',
                'slug': 'sony',
                'description': 'Entertainment and electronics innovation',
                'is_featured': True
            },
            {
                'name': 'LG',
                'slug': 'lg',
                'description': 'Home appliances and electronics',
                'is_featured': False
            },
            {
                'name': 'HP',
                'slug': 'hp',
                'description': 'Computing and printing solutions',
                'is_featured': False
            },
            {
                'name': 'Dell',
                'slug': 'dell',
                'description': 'Computer technology and solutions',
                'is_featured': False
            }
        ]
        
        for brand_data in brands_data:
            brand, created = Brand.objects.get_or_create(
                name=brand_data['name'],
                defaults=brand_data
            )
            if created:
                self.stdout.write(f'Created brand: {brand.name}')

    def create_flash_sales(self):
        """Create sample flash sales"""
        flash_sales_data = [
            {
                'name': 'Weekend Flash Sale',
                'description': 'Amazing deals for the weekend! Up to 50% off on selected items.',
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=2),
                'discount_percentage': Decimal('25.00'),
                'is_active': True
            },
            {
                'name': 'Electronics Mega Sale',
                'description': 'Huge discounts on electronics and gadgets.',
                'start_date': timezone.now() + timedelta(days=7),
                'end_date': timezone.now() + timedelta(days=10),
                'discount_percentage': Decimal('30.00'),
                'is_active': True
            },
            {
                'name': 'Fashion Week Special',
                'description': 'Exclusive fashion deals you cannot miss!',
                'start_date': timezone.now() + timedelta(days=14),
                'end_date': timezone.now() + timedelta(days=17),
                'discount_percentage': Decimal('40.00'),
                'is_active': True
            }
        ]
        
        for sale_data in flash_sales_data:
            sale, created = FlashSale.objects.get_or_create(
                name=sale_data['name'],
                defaults=sale_data
            )
            if created:
                self.stdout.write(f'Created flash sale: {sale.name}')

    def create_loyalty_program(self):
        """Create loyalty program"""
        program, created = LoyaltyProgram.objects.get_or_create(
            name="Vintage Rewards",
            defaults={
                'description': 'Earn points on every purchase and redeem for discounts!',
                'points_per_dollar': Decimal('1.00'),
                'min_points_to_redeem': 100,
                'point_value': Decimal('0.01'),
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created loyalty program: {program.name}')

    def create_notification_types(self):
        """Create notification types"""
        notification_types = [
            {
                'name': 'order_placed',
                'description': 'New order placed notification',
                'is_active': True
            },
            {
                'name': 'order_shipped',
                'description': 'Order shipped notification',
                'is_active': True
            },
            {
                'name': 'order_delivered',
                'description': 'Order delivered notification',
                'is_active': True
            },
            {
                'name': 'flash_sale',
                'description': 'Flash sale notification',
                'is_active': True
            },
            {
                'name': 'loyalty_reward',
                'description': 'Loyalty points earned notification',
                'is_active': True
            },
            {
                'name': 'product_review',
                'description': 'New product review notification',
                'is_active': True
            },
            {
                'name': 'low_stock',
                'description': 'Low stock alert notification',
                'is_active': True
            },
            {
                'name': 'price_drop',
                'description': 'Price drop alert notification',
                'is_active': True
            }
        ]
        
        for nt_data in notification_types:
            nt, created = NotificationType.objects.get_or_create(
                name=nt_data['name'],
                defaults=nt_data
            )
            if created:
                self.stdout.write(f'Created notification type: {nt.name}')

    def create_product_attributes(self):
        """Create product attributes"""
        attributes_data = [
            {
                'name': 'color',
                'display_name': 'Color',
                'attribute_type': 'select',
                'is_required': False,
                'options': ['Red', 'Blue', 'Green', 'Black', 'White', 'Yellow', 'Purple', 'Orange']
            },
            {
                'name': 'size',
                'display_name': 'Size',
                'attribute_type': 'select',
                'is_required': False,
                'options': ['XS', 'S', 'M', 'L', 'XL', 'XXL']
            },
            {
                'name': 'material',
                'display_name': 'Material',
                'attribute_type': 'text',
                'is_required': False
            },
            {
                'name': 'warranty',
                'display_name': 'Warranty Period',
                'attribute_type': 'text',
                'is_required': False
            },
            {
                'name': 'brand_model',
                'display_name': 'Model Number',
                'attribute_type': 'text',
                'is_required': False
            },
            {
                'name': 'storage',
                'display_name': 'Storage Capacity',
                'attribute_type': 'select',
                'is_required': False,
                'options': ['16GB', '32GB', '64GB', '128GB', '256GB', '512GB', '1TB']
            },
            {
                'name': 'screen_size',
                'display_name': 'Screen Size',
                'attribute_type': 'select',
                'is_required': False,
                'options': ['5.5"', '6.1"', '6.5"', '6.7"', '13"', '15"', '17"', '21"', '24"', '27"']
            }
        ]
        
        for attr_data in attributes_data:
            attr, created = ProductAttribute.objects.get_or_create(
                name=attr_data['name'],
                defaults=attr_data
            )
            if created:
                self.stdout.write(f'Created product attribute: {attr.display_name}')

    def create_sample_vendors(self):
        """Create sample vendor users"""
        vendors_data = [
            {
                'username': 'techstore_ng',
                'email': 'tech@example.com',
                'first_name': 'Tech',
                'last_name': 'Store',
                'password': 'vendor123'
            },
            {
                'username': 'fashion_hub',
                'email': 'fashion@example.com',
                'first_name': 'Fashion',
                'last_name': 'Hub',
                'password': 'vendor123'
            },
            {
                'username': 'home_essentials',
                'email': 'home@example.com',
                'first_name': 'Home',
                'last_name': 'Essentials',
                'password': 'vendor123'
            }
        ]
        
        for vendor_data in vendors_data:
            if not User.objects.filter(username=vendor_data['username']).exists():
                user = User.objects.create_user(
                    username=vendor_data['username'],
                    email=vendor_data['email'],
                    first_name=vendor_data['first_name'],
                    last_name=vendor_data['last_name'],
                    password=vendor_data['password']
                )
                self.stdout.write(f'Created vendor user: {user.username}')

    def create_sample_products(self):
        """Create sample products"""
        # Get categories, brands, and vendors
        categories = Category.objects.filter(type='product')
        brands = Brand.objects.all()
        vendors = User.objects.filter(username__in=['techstore_ng', 'fashion_hub', 'home_essentials'])
        
        if not categories.exists() or not brands.exists() or not vendors.exists():
            self.stdout.write('Please create categories, brands, and vendors first')
            return
        
        products_data = [
            {
                'name': 'iPhone 15 Pro Max',
                'description': 'Latest iPhone with advanced camera system and A17 Pro chip.',
                'price': Decimal('1200000.00'),
                'regular_price': Decimal('1350000.00'),
                'stock': 50,
                'brand': 'Apple',
                'category_type': 'Electronics',
                'vendor': 'techstore_ng',
                'featured': True,
                'tags': 'smartphone, apple, iphone, mobile'
            },
            {
                'name': 'Samsung Galaxy S24 Ultra',
                'description': 'Premium Android smartphone with S Pen and advanced AI features.',
                'price': Decimal('1100000.00'),
                'regular_price': Decimal('1200000.00'),
                'stock': 30,
                'brand': 'Samsung',
                'category_type': 'Electronics',
                'vendor': 'techstore_ng',
                'featured': True,
                'tags': 'smartphone, samsung, galaxy, android'
            },
            {
                'name': 'Nike Air Max 270',
                'description': 'Comfortable running shoes with Max Air cushioning.',
                'price': Decimal('85000.00'),
                'regular_price': Decimal('95000.00'),
                'stock': 100,
                'brand': 'Nike',
                'category_type': 'Fashion',
                'vendor': 'fashion_hub',
                'featured': True,
                'tags': 'shoes, nike, running, sports'
            },
            {
                'name': 'MacBook Pro 16-inch',
                'description': 'Powerful laptop for professionals with M3 Pro chip.',
                'price': Decimal('2500000.00'),
                'regular_price': Decimal('2700000.00'),
                'stock': 15,
                'brand': 'Apple',
                'category_type': 'Electronics',
                'vendor': 'techstore_ng',
                'featured': True,
                'tags': 'laptop, apple, macbook, computer'
            },
            {
                'name': 'Sony WH-1000XM5 Headphones',
                'description': 'Premium noise-canceling wireless headphones.',
                'price': Decimal('350000.00'),
                'regular_price': Decimal('400000.00'),
                'stock': 75,
                'brand': 'Sony',
                'category_type': 'Electronics',
                'vendor': 'techstore_ng',
                'featured': False,
                'tags': 'headphones, sony, wireless, audio'
            },
            {
                'name': 'Adidas Ultraboost 22',
                'description': 'High-performance running shoes with Boost technology.',
                'price': Decimal('120000.00'),
                'regular_price': Decimal('140000.00'),
                'stock': 80,
                'brand': 'Adidas',
                'category_type': 'Fashion',
                'vendor': 'fashion_hub',
                'featured': False,
                'tags': 'shoes, adidas, running, boost'
            }
        ]
        
        for product_data in products_data:
            # Get related objects
            try:
                brand = brands.get(name=product_data['brand'])
                category = categories.filter(title__icontains=product_data['category_type']).first()
                vendor = vendors.get(username=product_data['vendor'])
                
                if not category:
                    continue
                
                product, created = Product.objects.get_or_create(
                    name=product_data['name'],
                    defaults={
                        'description': product_data['description'],
                        'price': product_data['price'],
                        'regular_price': product_data['regular_price'],
                        'stock': product_data['stock'],
                        'brand': brand,
                        'category': category,
                        'vendor': vendor,
                        'featured': product_data['featured'],
                        'tags': product_data['tags'],
                        'status': 'Published',
                        'view_count': random.randint(50, 500)
                    }
                )
                
                if created:
                    self.stdout.write(f'Created product: {product.name}')
                    
            except Exception as e:
                self.stdout.write(f'Error creating product {product_data["name"]}: {e}')

    def create_sample_bundles(self):
        """Create sample product bundles"""
        products = Product.objects.all()
        
        if products.count() < 4:
            self.stdout.write('Not enough products to create bundles')
            return
        
        bundles_data = [
            {
                'name': 'Tech Starter Bundle',
                'description': 'Perfect bundle for tech enthusiasts - smartphone and headphones.',
                'discount_percentage': Decimal('15.00'),
                'is_active': True,
                'product_names': ['iPhone 15 Pro Max', 'Sony WH-1000XM5 Headphones']
            },
            {
                'name': 'Runner\'s Bundle',
                'description': 'Everything you need for running - shoes from top brands.',
                'discount_percentage': Decimal('20.00'),
                'is_active': True,
                'product_names': ['Nike Air Max 270', 'Adidas Ultraboost 22']
            }
        ]
        
        for bundle_data in bundles_data:
            bundle, created = Bundle.objects.get_or_create(
                name=bundle_data['name'],
                defaults={
                    'description': bundle_data['description'],
                    'discount_percentage': bundle_data['discount_percentage'],
                    'is_active': bundle_data['is_active']
                }
            )
            
            if created:
                self.stdout.write(f'Created bundle: {bundle.name}')
                
                # Add products to bundle
                for product_name in bundle_data['product_names']:
                    try:
                        product = products.get(name=product_name)
                        BundleItem.objects.create(
                            bundle=bundle,
                            product=product,
                            quantity=1
                        )
                    except Product.DoesNotExist:
                        continue

    def create_customer_segments(self):
        """Create customer segments"""
        segments_data = [
            {
                'name': 'New Customers',
                'segment_type': 'new_customer',
                'description': 'Customers who joined in the last 30 days',
                'criteria': {'days_since_joined': 30, 'max_orders': 1},
                'is_active': True
            },
            {
                'name': 'VIP Customers',
                'segment_type': 'vip_customer',
                'description': 'High-value customers with significant purchase history',
                'criteria': {'min_total_spent': 500000, 'min_orders': 10},
                'is_active': True
            },
            {
                'name': 'At Risk Customers',
                'segment_type': 'at_risk',
                'description': 'Customers who haven\'t ordered in 60+ days',
                'criteria': {'days_since_last_order': 60, 'min_orders': 2},
                'is_active': True
            },
            {
                'name': 'High Value Customers',
                'segment_type': 'high_value',
                'description': 'Customers with high lifetime value',
                'criteria': {'min_total_spent': 200000},
                'is_active': True
            },
            {
                'name': 'Regular Customers',
                'segment_type': 'regular_customer',
                'description': 'Customers with consistent purchase behavior',
                'criteria': {'min_orders': 3, 'max_days_since_last_order': 90},
                'is_active': True
            }
        ]
        
        for segment_data in segments_data:
            segment, created = CustomerSegment.objects.get_or_create(
                name=segment_data['name'],
                defaults=segment_data
            )
            if created:
                self.stdout.write(f'Created customer segment: {segment.name}')

        self.stdout.write(
            self.style.SUCCESS(
                '\n🎉 Sample data creation completed!\n'
                'Created:\n'
                f'- {Brand.objects.count()} brands\n'
                f'- {FlashSale.objects.count()} flash sales\n'
                f'- {LoyaltyProgram.objects.count()} loyalty program\n'
                f'- {NotificationType.objects.count()} notification types\n'
                f'- {ProductAttribute.objects.count()} product attributes\n'
                f'- {Product.objects.count()} products\n'
                f'- {Bundle.objects.count()} bundles\n'
                f'- {CustomerSegment.objects.count()} customer segments\n'
            )
        )