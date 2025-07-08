from django.core.management.base import BaseCommand
from store.models import Category
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Seeds a full marketplace-style category tree like Jumia, Amazon, etc.'

    def handle(self, *args, **options):
        categories = {
            "Furniture and Fittings": [
                "Kitchens",
                "Gardenings",
                "Beddings",
                "Sofas"
            ],
            "Fashion": [
                "Men's Clothing",
                "Men's Shoes",
                "Watches & Accessories",
                "Women's Clothing",
                "Women's Shoes",
                "Children Wears",
                "Bags & Handbags",
                "Jewelry",
                "Underwear",
                "Traditional Wear",
                "Eyewear"
            ],
            "Building Materials": [
                "Electrical & Solar System",
                "Plumbings",
                "Cements",
                "Roofing Materials",
                "Doors & Windows"
            ],
            "Trucks & Vehicles": [
                "Mercedes Benz",
                "BMW",
                "Toyota",
                "Hyundai",
                "Honda",
                "Volkswagen",
                "Ford",
                "Chevrolet",
                "Lexus",
                "New Vehicles",
                "Used Vehicles",
                "Motorcycles",
                "Spare Parts"
            ],
            "Agricultural": [
                "Fertilizer & Chemicals",
                "Tractors & Farming Equipment", 
                "Grains & Vegetables",
                "Poultry, Animals & Animals Feeds",
                "Veterinary", 
                "Pets"
            ],
            "Aviation": [
                "Aircrafts",
                "Ground Handling Equipment ",
                "Airline Tickets & Bookings "
            ],
            "Shipping": [
                "VLCC",
                "Clearing & Forwarding",
                "Ports & Inland Dry Ports",
                "Cleaning Items",
                "Breakfast",
                "Grains & Pasta",
                "Cooking Ingredients"
            ],
            "Lands & Houses": [
                "Abuja",
                "Abia",
                "Adamawa",
                "Akwa Ibom",
                "Anambra",
                "Bauchi",
                "Bayelsa",
                "Benue",
                "Borno",
                "Cross",
                "Delta",
                "Ebonyi",
                "Edo",
                "Ekiti",
                "Enugu",
                "Gombe",
                "Imo",
                "Jigawa",
                "Kaduna",
                "Kano",
                "Katsina",
                "Kebbi",
                "Kogi",
                "Kwara",
                "Lagos",
                "Nassarawa",
                "Niger",
                "Ogun",
                "Ondo",
                "Osun",
                "Oyo",
                "Plateau"
                "Rivers",
                "Sokoto",
                "Taraba",
                "Yobe",
                "Zamfara"
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
