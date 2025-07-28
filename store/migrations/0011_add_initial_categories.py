# Generated manually

from django.db import migrations
from django.utils.text import slugify


def add_initial_categories(apps, schema_editor):
    Category = apps.get_model('store', 'Category')
    
    # Helper function to create a category
    def create_category(title, parent=None, description=None, icon=None, order=0, is_featured=False):
        slug = slugify(title)
        # Check if the category already exists
        if Category.objects.filter(slug=slug).exists():
            return Category.objects.get(slug=slug)
        
        category = Category(
            title=title,
            slug=slug,
            parent=parent,
            description=description,
            icon=icon,
            order=order,
            is_featured=is_featured
        )
        category.save()
        return category
    
    # Create main categories
    lands_house = create_category("Lands and House", icon="fa-home", is_featured=True, order=1)
    building_materials = create_category("Building materials", icon="fa-tools", order=2)
    trucks_vehicles = create_category("Trucks and vehicles", icon="fa-car", is_featured=True, order=3)
    fashion = create_category("Fashion and Children's wears", icon="fa-tshirt", is_featured=True, order=4)
    jobs = create_category("Jobs and vacancies", icon="fa-briefcase", order=5)
    furniture = create_category("Furniture and fittings", icon="fa-couch", order=6)
    agricultural = create_category("Agricultural", icon="fa-tractor", order=7)
    aviation = create_category("Aviation", icon="fa-plane", order=8)
    shipping = create_category("Shipping", icon="fa-ship", order=9)
    oils_gas = create_category("Oils and Gas", icon="fa-gas-pump", order=10)
    professional_service = create_category("Professional service", icon="fa-user-tie", order=11)
    contracts = create_category("Contracts and JV", icon="fa-handshake", order=12)
    equipments = create_category("Equipments", icon="fa-tools", order=13)
    yellow_pages = create_category("Yellow pages", icon="fa-book", order=14)
    maritals = create_category("Maritals", icon="fa-heart", order=15)
    rents = create_category("Rents", icon="fa-key", order=16)
    events = create_category("Events", icon="fa-calendar", order=17)
    business_news = create_category("Business news", icon="fa-newspaper", order=18)
    classified = create_category("Classified adverts", icon="fa-ad", order=19)
    computers = create_category("Computers", icon="fa-laptop", is_featured=True, order=20)
    sporting = create_category("Sporting goods", icon="fa-futbol", order=21)
    perfumes = create_category("Perfumes and Cosmetics", icon="fa-spray-can", order=22)
    gold = create_category("Gold and Jewellery", icon="fa-gem", order=23)
    toys = create_category("Toys and Games", icon="fa-gamepad", order=24)
    phones = create_category("Phones and Tablets", icon="fa-mobile-alt", is_featured=True, order=25)
    appliances = create_category("Appliances", icon="fa-blender", order=26)
    paybills = create_category("Paybills", icon="fa-money-bill", order=27)
    supermarket = create_category("Supermarket", icon="fa-shopping-cart", is_featured=True, order=28)
    mining = create_category("Mining", icon="fa-hard-hat", order=29)
    medicals = create_category("Medicals and Pharmaceuticals", icon="fa-pills", order=30)
    education = create_category("Education", icon="fa-graduation-cap", order=31)
    transportation = create_category("Transportation", icon="fa-bus", order=32)
    security = create_category("Security and Safety", icon="fa-shield-alt", order=33)
    foods = create_category("Foods and Restaurants", icon="fa-utensils", is_featured=True, order=34)
    media = create_category("Media and Publicity", icon="fa-bullhorn", order=35)
    finance = create_category("Finance and Insurance", icon="fa-money-check", order=36)
    
    # Create subcategories for Lands and House
    state = create_category("State", parent=lands_house)
    create_category("Abuja FCT", parent=state)
    create_category("Lagos", parent=state)
    create_category("Kaduna", parent=state)
    create_category("Kano", parent=state)
    
    local_govt = create_category("Local Government", parent=lands_house)
    create_category("AMAC", parent=local_govt)
    create_category("BWARI", parent=local_govt)
    create_category("IKEJA", parent=local_govt)
    
    location = create_category("Location", parent=lands_house)
    create_category("Maitama", parent=location)
    create_category("Guzape", parent=location)
    
    # Create subcategories for Building materials
    create_category("Electrical", parent=building_materials)
    create_category("Plumbings", parent=building_materials)
    create_category("Cements", parent=building_materials)
    create_category("Roofing materials", parent=building_materials)
    create_category("Doors and Windows", parent=building_materials)
    
    # Create subcategories for Trucks and vehicles
    brand = create_category("Brand", parent=trucks_vehicles)
    create_category("Toyota", parent=brand)
    create_category("Mercedes", parent=brand)
    create_category("BMW", parent=brand)
    
    create_category("New vehicles", parent=trucks_vehicles)
    create_category("Used vehicles", parent=trucks_vehicles)
    create_category("Motorcycles", parent=trucks_vehicles)
    create_category("Spares parts", parent=trucks_vehicles)
    
    # Create subcategories for Fashion and Children's wears
    create_category("Men's Fashion", parent=fashion)
    create_category("Ladies Fashion", parent=fashion)
    
    # Create subcategories for Furniture and fittings
    create_category("Kitchens", parent=furniture)
    create_category("Gardening", parent=furniture)
    create_category("Beddings", parent=furniture)
    create_category("Sofas", parent=furniture)
    
    # Create subcategories for Agricultural
    create_category("Fertilizer and Chemicals", parent=agricultural)
    create_category("Tractors and Farming equipment", parent=agricultural)
    create_category("Grains and Vegetables", parent=agricultural)
    create_category("Poultry, Animals and Animal feeds", parent=agricultural)
    create_category("Veterinary", parent=agricultural)
    create_category("Pets", parent=agricultural)
    
    # Create subcategories for Aviation
    create_category("Aircrafts", parent=aviation)
    create_category("Ground Handling Equipment", parent=aviation)
    create_category("Airline Tickets and Bookings", parent=aviation)
    
    # Create subcategories for Shipping
    create_category("VLCC", parent=shipping)
    create_category("Clearing and Forwarding", parent=shipping)
    create_category("Ports and Inland Dry Ports", parent=shipping)
    create_category("Containers", parent=shipping)
    
    # Create subcategories for Professional service
    create_category("Skilled and Unskilled workers", parent=professional_service)
    create_category("Legal services", parent=professional_service)
    create_category("Architecture", parent=professional_service)
    create_category("IT", parent=professional_service)
    create_category("Immigration and Visas", parent=professional_service)
    create_category("Employment Agency", parent=professional_service)
    
    # Create subcategories for Paybills
    create_category("Electricity", parent=paybills)
    create_category("TV", parent=paybills)
    create_category("Airtime", parent=paybills)
    
    # Create subcategories for Mining
    create_category("Mining Equipment", parent=mining)
    create_category("Mineral", parent=mining)
    
    # Create subcategories for Medicals and Pharmaceuticals
    create_category("Health and Beauty", parent=medicals)
    create_category("Saloons and Spas", parent=medicals)
    create_category("Medical Equipment and consumables", parent=medicals)
    create_category("Pharmacies and Chemist", parent=medicals)
    create_category("Hospital and Clinics", parent=medicals)
    create_category("Medical Laboratory", parent=medicals)
    
    # Create subcategories for Education
    create_category("Schools", parent=education)
    create_category("Educational materials", parent=education)
    create_category("Books and Journals", parent=education)
    
    # Create subcategories for Transportation
    create_category("Car hire service", parent=transportation)
    create_category("Rent a Car", parent=transportation)
    create_category("Luxurious buses", parent=transportation)
    create_category("Moving Equipments", parent=transportation)
    
    # Create subcategories for Security and Safety
    create_category("Escorts", parent=security)
    create_category("Security Guards", parent=security)
    create_category("Security Equipment", parent=security)
    create_category("Safety equipment", parent=security)
    
    # Create subcategories for Foods and Restaurants
    create_category("Outdoor catering", parent=foods)
    create_category("Event Centres", parent=foods)
    create_category("Events Planning", parent=foods)
    
    # Create subcategories for Media and Publicity
    create_category("Outdoor Advertising", parent=media)
    create_category("Electronic and Print media", parent=media)
    create_category("Printers and Printing Materials", parent=media)
    
    # Create subcategories for Finance and Insurance
    create_category("Insurance Brokers", parent=finance)
    create_category("Trifts and Loans", parent=finance)


def remove_initial_categories(apps, schema_editor):
    Category = apps.get_model('store', 'Category')
    Category.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_add_category_fields'),
    ]

    operations = [
        migrations.RunPython(add_initial_categories, remove_initial_categories),
    ]