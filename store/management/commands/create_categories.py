from django.core.management.base import BaseCommand
from store.models import Category

class Command(BaseCommand):
    help = 'Create comprehensive categories for Vintage ecommerce'

    def handle(self, *args, **options):
        categories_data = [
            # Electronics & Technology
            {
                'title': 'Electronics & Technology',
                'slug': 'electronics-technology',
                'type': 'product',
                'is_featured': True,
                'order': 1,
                'subcategories': [
                    'Smartphones & Tablets',
                    'Laptops & Computers',
                    'Audio & Headphones',
                    'Cameras & Photography',
                    'Gaming & Consoles',
                    'Smart Home & IoT',
                    'Wearable Technology',
                    'Accessories & Cables'
                ]
            },
            
            # Fashion & Apparel
            {
                'title': 'Fashion & Apparel',
                'slug': 'fashion-apparel',
                'type': 'product',
                'is_featured': True,
                'order': 2,
                'subcategories': [
                    'Men\'s Clothing',
                    'Women\'s Clothing',
                    'Kids & Baby',
                    'Shoes & Footwear',
                    'Bags & Accessories',
                    'Jewelry & Watches',
                    'Sunglasses & Eyewear',
                    'Vintage & Retro'
                ]
            },
            
            # Home & Living
            {
                'title': 'Home & Living',
                'slug': 'home-living',
                'type': 'product',
                'is_featured': True,
                'order': 3,
                'subcategories': [
                    'Furniture',
                    'Home Decor',
                    'Kitchen & Dining',
                    'Bedding & Bath',
                    'Lighting',
                    'Storage & Organization',
                    'Garden & Outdoor',
                    'Appliances'
                ]
            },
            
            # Health & Beauty
            {
                'title': 'Health & Beauty',
                'slug': 'health-beauty',
                'type': 'product',
                'is_featured': True,
                'order': 4,
                'subcategories': [
                    'Skincare',
                    'Makeup & Cosmetics',
                    'Hair Care',
                    'Fragrances',
                    'Health Supplements',
                    'Personal Care',
                    'Fitness Equipment',
                    'Medical Supplies'
                ]
            },
            
            # Sports & Outdoors
            {
                'title': 'Sports & Outdoors',
                'slug': 'sports-outdoors',
                'type': 'product',
                'is_featured': True,
                'order': 5,
                'subcategories': [
                    'Fitness & Exercise',
                    'Team Sports',
                    'Water Sports',
                    'Cycling',
                    'Camping & Hiking',
                    'Winter Sports',
                    'Athletic Wear',
                    'Sports Accessories'
                ]
            },
            
            # Books & Media
            {
                'title': 'Books & Media',
                'slug': 'books-media',
                'type': 'product',
                'is_featured': False,
                'order': 6,
                'subcategories': [
                    'Books',
                    'E-books',
                    'Audiobooks',
                    'Movies & TV',
                    'Music',
                    'Video Games',
                    'Magazines',
                    'Educational Materials'
                ]
            },
            
            # Automotive
            {
                'title': 'Automotive',
                'slug': 'automotive',
                'type': 'product',
                'is_featured': False,
                'order': 7,
                'subcategories': [
                    'Car Parts & Accessories',
                    'Motorcycle Parts',
                    'Tools & Equipment',
                    'Car Care',
                    'Electronics',
                    'Interior Accessories',
                    'Exterior Accessories',
                    'Tires & Wheels'
                ]
            },
            
            # Baby & Kids
            {
                'title': 'Baby & Kids',
                'slug': 'baby-kids',
                'type': 'product',
                'is_featured': True,
                'order': 8,
                'subcategories': [
                    'Baby Gear',
                    'Baby Clothing',
                    'Toys & Games',
                    'Kids Clothing',
                    'School Supplies',
                    'Baby Food & Formula',
                    'Strollers & Car Seats',
                    'Nursery Decor'
                ]
            },
            
            # Services (Listings)
            {
                'title': 'Professional Services',
                'slug': 'professional-services',
                'type': 'listing',
                'is_featured': True,
                'order': 9,
                'subcategories': [
                    'Web Development',
                    'Graphic Design',
                    'Digital Marketing',
                    'Writing & Translation',
                    'Business Consulting',
                    'Legal Services',
                    'Accounting & Finance',
                    'Photography & Video'
                ]
            },
            
            # Real Estate
            {
                'title': 'Real Estate',
                'slug': 'real-estate',
                'type': 'listing',
                'is_featured': True,
                'order': 10,
                'subcategories': [
                    'Houses for Sale',
                    'Apartments for Rent',
                    'Commercial Properties',
                    'Land & Plots',
                    'Vacation Rentals',
                    'Office Spaces',
                    'Warehouses',
                    'Investment Properties'
                ]
            },
            
            # Vehicles
            {
                'title': 'Vehicles',
                'slug': 'vehicles',
                'type': 'listing',
                'is_featured': True,
                'order': 11,
                'subcategories': [
                    'Cars',
                    'Motorcycles',
                    'Trucks & Vans',
                    'Boats & Marine',
                    'RVs & Campers',
                    'ATVs & UTVs',
                    'Classic Cars',
                    'Electric Vehicles'
                ]
            },
            
            # Jobs & Career
            {
                'title': 'Jobs & Career',
                'slug': 'jobs-career',
                'type': 'listing',
                'is_featured': False,
                'order': 12,
                'subcategories': [
                    'Full-time Jobs',
                    'Part-time Jobs',
                    'Freelance Work',
                    'Internships',
                    'Remote Work',
                    'Contract Work',
                    'Executive Positions',
                    'Entry Level'
                ]
            }
        ]
        
        for cat_data in categories_data:
            # Create parent category
            parent_cat, created = Category.objects.get_or_create(
                title=cat_data['title'],
                defaults={
                    'slug': cat_data['slug'],
                    'type': cat_data['type'],
                    'is_featured': cat_data['is_featured'],
                    'order': cat_data['order']
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created parent category: {parent_cat.title}')
                )
            
            # Create subcategories
            for i, subcat_title in enumerate(cat_data['subcategories']):
                subcat_slug = subcat_title.lower().replace(' ', '-').replace('&', 'and').replace("'", "")
                subcat, sub_created = Category.objects.get_or_create(
                    title=subcat_title,
                    parent=parent_cat,
                    defaults={
                        'slug': f"{parent_cat.slug}-{subcat_slug}",
                        'type': cat_data['type'],
                        'order': i + 1
                    }
                )
                
                if sub_created:
                    self.stdout.write(
                        self.style.SUCCESS(f'  Created subcategory: {subcat.title}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created all categories!')
        )