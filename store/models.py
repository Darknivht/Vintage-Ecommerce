from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from cloudinary.models import CloudinaryField

from userauths import models as user_models
from vendor import models as vendor_models

import shortuuid

STATUS = (
    ("Published", "Published"),
    ("Draft", "Draft"),
    ("Disabled", "Disabled"),
)

PAYMENT_STATUS = (
    ("Paid", "Paid"),
    ("Processing", "Processing"),
    ("Failed", 'Failed'),
)

PAYMENT_METHOD = (
    ("PayPal", "PayPal"),
    ("Stripe", "Stripe"),
    ("Flutterwave", "Flutterwave"),
    ("Paystack", "Paystack"),
    ("RazorPay", "RazorPay"),
)

ORDER_STATUS = (
    ("Pending", "Pending"),
    ("Processing", "Processing"),
    ("Shipped", "Shipped"),
    ("Fulfilled", "Fulfilled"),
    ("Cancelled", "Cancelled"),
)

SHIPPING_SERVICE = (
    ("DHL", "DHL"),
    ("FedX", "FedX"),
    ("UPS", "UPS"),
    ("GIG Logistics", "GIG Logistics")
)


RATING = (
    ( 1,  "★☆☆☆☆"),
    ( 2,  "★★☆☆☆"),
    ( 3,  "★★★☆☆"),
    ( 4,  "★★★★☆"),
    ( 5,  "★★★★★"),
)

class Category(models.Model):
    title = models.CharField(max_length=100, blank=False)
    image = CloudinaryField(folder="images", null=True, blank=True)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="subcategories")
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Font Awesome icon class")
    order = models.IntegerField(default=0, help_text="Order in which to display this category")
    is_featured = models.BooleanField(default=False, help_text="Whether to feature this category on the homepage")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'title']

    def __str__(self):
        if self.parent:
            return f"{self.parent.title} > {self.title}"
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('store:category', args=[self.slug])

    def get_full_path(self):
        """Return the full path of the category (e.g. 'Parent > Child > Grandchild')"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.title}"
        return self.title

    def get_level(self):
        """Return the level of the category in the hierarchy (0 for top-level)"""
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level

    def all_products(self):
        """Return all products in this category and its subcategories"""
        subcategories = self.subcategories.all()
        return Product.objects.filter(category__in=[self] + list(subcategories))

    def products(self):
        """Return only products directly in this category"""
        return Product.objects.filter(category=self)

    def get_all_subcategories(self):
        """Return all subcategories recursively"""
        all_subcategories = list(self.subcategories.all())
        for subcategory in self.subcategories.all():
            all_subcategories.extend(subcategory.get_all_subcategories())
        return all_subcategories

    def get_siblings(self):
        """Return all categories with the same parent"""
        if self.parent:
            return Category.objects.filter(parent=self.parent).exclude(id=self.id)
        return Category.objects.filter(parent__isnull=True).exclude(id=self.id)

    
class Product(models.Model):
    name = models.CharField(max_length=100)
    image = CloudinaryField(folder="images", blank=True, null=True)
    description = CKEditor5Field('Text', config_name='extends')
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, verbose_name="Sale Price")
    regular_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, verbose_name="Regular Price")

    stock = models.PositiveIntegerField(default=0, null=True, blank=True)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, verbose_name="Shipping Amount")
    
    status = models.CharField(choices=STATUS, max_length=50, default="Published")
    featured = models.BooleanField(default=False, verbose_name="Marketplace Featured")
    
    vendor = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True)
    
    sku = ShortUUIDField(unique=True, length=5, max_length=50, prefix="SKU", alphabet="1234567890")
    slug = models.SlugField(null=True, blank=True)
    
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-id']
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name
    
    def average_rating(self):
        return Review.objects.filter(product=self).aggregate(avg_rating=models.Avg('rating'))['avg_rating']
    
    def reviews(self):
        return Review.objects.filter(product=self)

    def gallery(self):
        return Gallery.objects.filter(product=self)
  
    def variants(self):
        return Variant.objects.filter(product=self)

    def vendor_orders(self):
        return OrderItem.objects.filter(product=self, vendor=self.vendor)

    def save(self, *args, **kwargs):
        if not self.slug :
            self.slug = slugify(self.name) + "-" + str(shortuuid.uuid().lower()[:2])
            
        super(Product, self).save(*args, **kwargs) 

class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=1000, verbose_name="Variant Name", null=True, blank=True)

    def items(self):
        return VariantItem.objects.filter(variant=self)
    
    def __str__(self):
        return self.name

class VariantItem(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='variant_items')
    title = models.CharField(max_length=1000, verbose_name="Item Title", null=True, blank=True)
    content = models.CharField(max_length=1000, verbose_name="Item Content", null=True, blank=True)

    def __str__(self):
        return self.variant.name
    
class Gallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    image = CloudinaryField(folder="images")
    gallery_id = ShortUUIDField(length=6, max_length=10, alphabet="1234567890")

    def __str__(self):
        return f"{self.product.name} - image"

class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True)
    qty = models.PositiveIntegerField(default=0, null=True, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)
    sub_total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)
    shipping = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)
    total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    cart_id = models.CharField(max_length=1000, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.cart_id} - {self.product.name}'

class Coupon(models.Model):
    vendor = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=100)
    discount = models.IntegerField(default=1)
    
    def __str__(self):
        return self.code

class Order(models.Model):
    vendors = models.ManyToManyField(user_models.User, blank=True)
    customer = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, related_name="customer", blank=True)
    sub_total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    shipping = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    payment_status = models.CharField(max_length=100, choices=PAYMENT_STATUS, default="Processing")
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD, default=None, null=True, blank=True)
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS, default="Pending")
    initial_total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, help_text="The original total before discounts")
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, help_text="Amount saved by customer")
    address = models.ForeignKey("customer.Address", on_delete=models.SET_NULL, null=True)
    coupons = models.ManyToManyField(Coupon, blank=True)
    order_id = ShortUUIDField(length=6, max_length=25, alphabet="1234567890")
    payment_id = models.CharField(null=True, blank=True, max_length=1000)
    date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Order"
        ordering = ['-date']

    def __str__(self):
        return self.order_id

    def order_items(self):
        return OrderItem.objects.filter(order=self)
    
    
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS, default="Pending")
    shipping_service = models.CharField(max_length=100, choices=SHIPPING_SERVICE, default=None, null=True, blank=True)
    tracking_id = models.CharField(max_length=100, default=None, null=True, blank=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField(default=0)
    color = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    initial_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Grand Total of all amount listed above before discount")
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, help_text="Amount saved by customer")
    coupon = models.ManyToManyField(Coupon, blank=True)
    applied_coupon = models.BooleanField(default=False)
    item_id = ShortUUIDField(length=6, max_length=25, alphabet="1234567890")
    vendor = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, related_name="vendor_order_items")
    date = models.DateTimeField(default=timezone.now)

    def order_id(self):
        return f"{self.order.order_id}"
  
    def __str__(self):
        return self.item_id
    
    class Meta:
        ordering = ['-date']

class Review(models.Model):
    user = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True, related_name="reviews")
    review = models.TextField(null=True, blank=True)
    reply = models.TextField(null=True, blank=True)
    rating = models.IntegerField(choices=RATING, default=None)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} review on {self.product.name}"


# Specialized Listing Models

VEHICLE_TYPES = (
    ("New", "New"),
    ("Used", "Used"),
    ("Motorcycle", "Motorcycle"),
    ("Spare Parts", "Spare Parts"),
)

class BaseListing(models.Model):
    """
    Abstract base model for all specialized listings
    """
    title = models.CharField(max_length=150)
    description = CKEditor5Field('Text', config_name='extends', null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=50, default="Published")
    slug = models.SlugField(null=True, blank=True)
    date_posted = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['-date_posted']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) + "-" + str(shortuuid.uuid().lower()[:4])
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class RealEstateListing(BaseListing):
    """
    Model for real estate listings (lands and houses)
    """
    state = models.CharField(max_length=100, null=True, blank=True)
    local_government = models.CharField(max_length=100, null=True, blank=True)
    neighborhood = models.CharField(max_length=150, null=True, blank=True)
    price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    land_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="In square meters or acres")
    house_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    number_of_bedrooms = models.IntegerField(null=True, blank=True)
    number_of_bathrooms = models.IntegerField(null=True, blank=True)
    images = CloudinaryField(folder="images", null=True, blank=True)


class VehicleListing(BaseListing):
    """
    Model for vehicle listings
    """
    brand = models.CharField(max_length=100, null=True, blank=True)
    vehicle_type = models.CharField(choices=VEHICLE_TYPES, max_length=100, default="Used")
    price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    mileage = models.IntegerField(null=True, blank=True, help_text="Mileage in kilometers")
    images = CloudinaryField(folder="images", null=True, blank=True)


class JobListing(BaseListing):
    """
    Model for job listings
    """
    company = models.CharField(max_length=150, null=True, blank=True)
    location = models.CharField(max_length=150, null=True, blank=True)
    salary_range = models.CharField(max_length=100, null=True, blank=True)
    application_link = models.URLField(null=True, blank=True)
    job_type = models.CharField(max_length=100, null=True, blank=True, help_text="Full-time, Part-time, Contract, etc")


class ServiceListing(BaseListing):
    """
    Model for service listings
    """
    service_type = models.CharField(max_length=150, null=True, blank=True)
    contact_phone = models.CharField(max_length=50, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    service_area = models.CharField(max_length=150, null=True, blank=True)


class Paybill(BaseListing):
    """
    Model for bill payment services
    """
    service_category = models.CharField(max_length=150, null=True, blank=True)
    payment_provider = models.CharField(max_length=150, null=True, blank=True)
    payment_code = models.CharField(max_length=50, null=True, blank=True)
