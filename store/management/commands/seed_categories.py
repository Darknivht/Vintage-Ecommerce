from django.core.management.base import BaseCommand
from store.models import Category
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Seeds a full marketplace-style category tree like Jumia, Amazon, etc.'

    def handle(self, *args, **options):
        categories = {
            "Electronics": [
                "Smartphones",
                "Tablet PCs",
                "Mobile Accessories",
                "Laptops",
                "Desktop Computers",
                "Printers & Scanners",
                "Computer Accessories",
                "Monitors",
                "Camera & Photography",
                "Projectors",
                "TV & Audio",
                "Video Games & Consoles",
            ],
            "Home Appliances": [
                "Refrigerators",
                "Freezers",
                "Air Conditioners",
                "Microwaves",
                "Washing Machines",
                "Vacuum Cleaners",
                "Blenders & Grinders",
                "Electric Kettles",
                "Toasters",
                "Fans & Heaters"
            ],
            "Fashion": [
                "Men's Clothing",
                "Men's Shoes",
                "Watches & Accessories",
                "Women's Clothing",
                "Women's Shoes",
                "Bags & Handbags",
                "Jewelry",
                "Underwear & Lingerie",
                "Traditional Wear",
                "Eyewear"
            ],
            "Gaming": [
                "PlayStation",
                "Xbox",
                "Nintendo",
                "Gaming Accessories",
                "Controllers & Gamepads",
                "Gaming Laptops",
                "Virtual Reality"
            ],
            "Health & Beauty": [
                "Fragrances",
                "Makeup",
                "Skincare",
                "Hair Care",
                "Bath & Body",
                "Men's Grooming",
                "Health & Wellness",
                "Vitamins & Supplements"
            ],
            "Baby, Kids & Toys": [
                "Baby Gear",
                "Diapers & Wipes",
                "Kids Clothing",
                "Toys & Games",
                "Feeding & Nursing",
                "Maternity Wear"
            ],
            "Home & Office": [
                "Furniture",
                "Kitchen & Dining",
                "Beddings",
                "Curtains & Blinds",
                "Lighting",
                "Decor",
                "Storage & Organization",
                "Office Equipment"
            ],
            "Grocery": [
                "Food Cupboard",
                "Beverages",
                "Household Supplies",
                "Cleaning Items",
                "Breakfast",
                "Grains & Pasta",
                "Cooking Ingredients"
            ],
            "Automobiles & Motorcycles": [
                "Cars",
                "Motorcycles",
                "Spare Parts",
                "Oils & Fluids",
                "Tyres & Rims",
                "Tools & Equipment",
                "GPS & Security"
            ],
            "Books, Music & Movies": [
                "Books",
                "Musical Instruments",
                "Educational Materials",
                "eBooks",
                "Movies & DVDs"
            ],
            "Sports & Fitness": [
                "Exercise & Fitness",
                "Indoor Games",
                "Outdoor Sports",
                "Sportswear",
                "Cycling",
                "Swimming",
                "Camping & Hiking"
            ],
            "Industrial & Scientific": [
                "Measurement & Test Tools",
                "Lab Equipment",
                "Industrial Supplies",
                "Security & Surveillance",
                "Safety Products"
            ],
            "Building Materials & Tools": [
                "Cement",
                "Paint & Coatings",
                "Doors & Windows",
                "Roofing Materials",
                "Solar Panels",
                "Power Tools",
                "Plumbing Materials",
                "Electrical Supplies"
            ],
            "Agriculture": [
                "Seeds & Fertilizers",
                "Farming Equipment",
                "Poultry & Livestock",
                "Animal Feeds",
                "Veterinary Supplies",
                "Tractors",
                "Grains & Produce"
            ],
            "Furniture & Fittings": [
                "Living Room Furniture",
                "Bedroom Furniture",
                "Office Furniture",
                "Kitchen Furniture",
                "Outdoor Furniture",
                "Decorative Items"
            ],
            "Jobs & Services": [
                "Job Vacancies",
                "Freelance Services",
                "Home Services",
                "Repair & Maintenance",
                "Tutoring & Education"
            ],
            "Aviation & Travel": [
                "Flight Bookings",
                "Aircraft Parts",
                "Ground Handling Equipment",
                "Charter Services"
            ],
            "Shipping & Logistics": [
                "Containers",
                "Shipping Vessels",
                "Delivery Services",
                "Freight & Forwarding",
                "Inland Dry Ports"
            ],
            "Pet Supplies": [
                "Pet Food",
                "Pet Toys",
                "Animal Health",
                "Pet Accessories"
            ],
        }

        created_count = 0

        for parent_title, sub_list in categories.items():
            parent_slug = slugify(parent_title)
            parent, created = Category.objects.get_or_create(
                title=parent_title,
                slug=parent_slug,
                parent=None
            )
            if created:
                created_count += 1

            for sub_title in sub_list:
                sub_slug = slugify(sub_title)
                sub, sub_created = Category.objects.get_or_create(
                    title=sub_title,
                    slug=sub_slug,
                    parent=parent
                )
                if sub_created:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ {created_count} categories and subcategories created successfully."))
