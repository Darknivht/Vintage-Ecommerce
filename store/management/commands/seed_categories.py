from django.core.management.base import BaseCommand
from store.models import Category
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Create categories and subcategories'

    def handle(self, *args, **options):
        def create_category(title, type="listing", parent=None):
            slug = slugify(title)
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={"title": title, "type": type, "parent": parent, "order": 0, "is_featured": False}
            )
            return category

        category_data = {
            "Lands and House": {
                "type": "listing",
                "subcategories": [
                    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno", "Cross River", "Delta",
                    "Ebonyi", "Edo", "Ekiti", "Enugu", "FCT (Abuja)", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina",
                    "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers",
                    "Sokoto", "Taraba", "Yobe", "Zamfara"
                ]
            },
            "Building Materials": {
                "type": "product",
                "subcategories": ["Electrical", "Plumbings", "Cements", "Roofing materials", "Doors and Windows"]
            },
            "Trucks and Vehicles": {
                "type": "listing",
                "subcategories": ["Toyota", "Mercedes", "BMW", "New Vehicles", "Used Vehicles", "Motorcycles", "Spare Parts"]
            },
            "Fashion and Children's Wears": {
                "type": "product",
                "subcategories": ["Men's Fashion", "Ladies Fashion"]
            },
            "Jobs and Vacancies": {"type": "listing", "subcategories": []},
            "Furniture and Fittings": {
                "type": "product",
                "subcategories": ["Kitchens", "Gardening", "Beddings", "Sofas"]
            },
            "Agricultural": {
                "type": "product",
                "subcategories": [
                    "Fertilizer and Chemicals", "Tractors and Farming Equipment", "Grains and Vegetables",
                    "Poultry, Animals and Animal Feeds", "Veterinary", "Pets"
                ]
            },
            "Aviation": {
                "type": "listing",
                "subcategories": ["Aircrafts", "Ground Handling Equipment", "Airline Tickets and Bookings"]
            },
            "Shipping": {
                "type": "listing",
                "subcategories": ["VLCC", "Clearing and Forwarding", "Ports and Inland Dry Ports", "Containers"]
            },
            "Oils and Gas": {"type": "listing", "subcategories": []},
            "Professional Service": {
                "type": "listing",
                "subcategories": [
                    "Skilled and Unskilled Workers", "Legal Services", "Architecture", "IT", "Immigration and Visas", "Employment Agency"
                ]
            },
            "Contracts and JV": {"type": "listing", "subcategories": []},
            "Equipments": {"type": "product", "subcategories": []},
            "Yellow Pages": {"type": "listing", "subcategories": []},
            "Maritals": {"type": "listing", "subcategories": []},
            "Rents": {"type": "listing", "subcategories": []},
            "Events": {"type": "listing", "subcategories": []},
            "Business News": {"type": "listing", "subcategories": []},
            "Classified Adverts": {"type": "listing", "subcategories": []},
            "Computers": {"type": "product", "subcategories": []},
            "Sporting Goods": {"type": "product", "subcategories": []},
            "Perfumes and Cosmetics": {"type": "product", "subcategories": []},
            "Gold and Jewellery": {"type": "product", "subcategories": []},
            "Toys and Games": {"type": "product", "subcategories": []},
            "Phones and Tablets": {"type": "product", "subcategories": []},
            "Appliances": {"type": "product", "subcategories": []},
            "Paybills": {
                "type": "product",
                "subcategories": ["Electricity", "TV", "Airtime"]
            },
            "Supermarket": {"type": "product", "subcategories": []},
            "Mining": {
                "type": "listing",
                "subcategories": ["Mining Equipment", "Mineral"]
            },
            "Medicals and Pharmaceuticals": {
                "type": "product",
                "subcategories": [
                    "Health and Beauty", "Saloons and Spas", "Medical Equipment and Consumables", "Pharmacies and Chemist",
                    "Hospital and Clinics", "Medical Laboratory"
                ]
            },
            "Education": {
                "type": "listing",
                "subcategories": ["Schools", "Educational Materials", "Books and Journals"]
            },
            "Transportation": {
                "type": "listing",
                "subcategories": ["Car Hire Service", "Rent a Car", "Luxurious Buses", "Moving Equipments"]
            },
            "Security and Safety": {
                "type": "listing",
                "subcategories": ["Escorts", "Security Guards", "Security Equipment", "Safety Equipment"]
            },
            "Foods and Restaurants": {
                "type": "listing",
                "subcategories": ["Outdoor Catering", "Event Centres", "Events Planning"]
            },
            "Media and Publicity": {
                "type": "listing",
                "subcategories": ["Outdoor Advertising", "Electronic and Print Media", "Printers and Printing Materials"]
            },
            "Finance and Insurance": {
                "type": "listing",
                "subcategories": ["Insurance Brokers", "Thrifts and Loans"]
            }
        }

        for parent_title, config in category_data.items():
            parent_cat = create_category(parent_title, type=config["type"])
            for sub_title in config.get("subcategories", []):
                create_category(sub_title, type=config["type"], parent=parent_cat)

        self.stdout.write(self.style.SUCCESS('✅ Categories and subcategories created successfully.'))
