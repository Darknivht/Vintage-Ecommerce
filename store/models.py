# models.py

from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from cloudinary.models import CloudinaryField

from userauths import models as user_models
from vendor import models as vendor_models

import shortuuid

# === CONSTANTS ===
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
    (1,  "★☆☆☆☆"),
    (2,  "★★☆☆☆"),
    (3,  "★★★☆☆"),
    (4,  "★★★★☆"),
    (5,  "★★★★★"),
)

# === CATEGORY MODELS ===
class Category(models.Model):
    CATEGORY_TYPE_CHOICES = (
        ("product", "Product"),
        ("listing", "Listing"),
    )

    title = models.CharField(max_length=100, blank=False)
    image = CloudinaryField(folder="images", null=True, blank=True)
    slug = models.SlugField(unique=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="subcategories")
    type = models.CharField(max_length=20, choices=CATEGORY_TYPE_CHOICES, default="product")

    class Meta:
        verbose_name_plural = "Categories"

    def all_products(self):
        subcategories = self.subcategories.all()
        return Product.objects.filter(category__in=[self] + list(subcategories))

    def __str__(self):
        return self.title

    def products(self):
        return Product.objects.filter(category=self)

    def listings(self):
        return Listing.objects.filter(category=self)


# NEW: Define dynamic schemas per category
class CategorySchema(models.Model):
    category = models.OneToOneField(Category, on_delete=models.CASCADE, related_name='schema')
    schema = models.JSONField(help_text="Dynamic metadata structure for this category (e.g. location, type, size)")

    def __str__(self):
        return f"Schema for {self.category.title}"


# === PRODUCT & LISTING MODELS ===
class Product(models.Model):
    name = models.CharField(max_length=100)
    image = CloudinaryField(folder="images", blank=True, null=True)
    description = CKEditor5Field('Text', config_name='extends')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    regular_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0, null=True, blank=True)
    min_stock_alert = models.PositiveIntegerField(default=5)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    dimensions = models.CharField(max_length=100, blank=True, help_text="L x W x H in cm")
    status = models.CharField(choices=STATUS, max_length=50, default="Published")
    featured = models.BooleanField(default=False)
    is_digital = models.BooleanField(default=False)
    vendor = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True)
    sku = ShortUUIDField(unique=True, length=5, max_length=50, prefix="SKU", alphabet="1234567890")
    slug = models.SlugField(null=True, blank=True)
    meta_title = models.CharField(max_length=160, blank=True)
    meta_description = models.TextField(max_length=320, blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    view_count = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-id']
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + "-" + str(shortuuid.uuid().lower()[:2])
        super(Product, self).save(*args, **kwargs)

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


# NEW: Flexible listing model for services, vehicles, lands, etc.
class Listing(models.Model):
    title = models.CharField(max_length=255)
    vendor = models.ForeignKey(user_models.User, on_delete=models.CASCADE, related_name='listings')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='listings')
    description = CKEditor5Field('Text', config_name='extends')
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    image = CloudinaryField(folder="listings", null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    slug = models.SlugField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) + "-" + shortuuid.uuid()[:6]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# === ENHANCED MODELS ===

# Enhanced Variant System
class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=1000, null=True, blank=True)
    price_adjustment = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    stock = models.PositiveIntegerField(default=0)
    sku = ShortUUIDField(length=8, max_length=50, prefix="VAR", alphabet="1234567890", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def items(self):
        return VariantItem.objects.filter(variant=self)
    
    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = shortuuid.uuid()[:8]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"

class VariantItem(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='variant_items')
    title = models.CharField(max_length=1000, null=True, blank=True)
    content = models.CharField(max_length=1000, null=True, blank=True)
    image = CloudinaryField(folder="variants", null=True, blank=True)
    
    def __str__(self):
        return f"{self.variant.name} - {self.title}"

# Product Attributes System
class ProductAttribute(models.Model):
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    is_required = models.BooleanField(default=False)
    attribute_type = models.CharField(max_length=20, choices=[
        ('text', 'Text'),
        ('number', 'Number'),
        ('select', 'Select'),
        ('multiselect', 'Multi Select'),
        ('boolean', 'Boolean'),
        ('color', 'Color'),
    ], default='text')
    
    def __str__(self):
        return self.display_name

class ProductAttributeValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    value = models.TextField()
    
    class Meta:
        unique_together = ('product', 'attribute')
    
    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}: {self.value}"

# Enhanced Brand System
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    logo = CloudinaryField(folder="brands", null=True, blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

# Flash Sales System
class FlashSale(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    banner_image = CloudinaryField(folder="flash_sales", null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    def is_live(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

class FlashSaleItem(models.Model):
    flash_sale = models.ForeignKey(FlashSale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity_limit = models.PositiveIntegerField(null=True, blank=True)
    sold_quantity = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('flash_sale', 'product')
    
    def __str__(self):
        return f"{self.flash_sale.name} - {self.product.name}"

# Bundle Deals System
class Bundle(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = CloudinaryField(folder="bundles", null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())
    
    def discounted_price(self):
        total = self.total_price()
        return total - (total * self.discount_percentage / 100)

class BundleItem(models.Model):
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.bundle.name} - {self.product.name}"

# Loyalty Program
class LoyaltyProgram(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)  # or models.CharField(max_length=255)
    points_per_dollar = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    min_points_to_redeem = models.PositiveIntegerField(default=100)
    point_value = models.DecimalField(max_digits=5, decimal_places=4, default=0.01)  # $0.01 per point
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class CustomerLoyaltyAccount(models.Model):
    customer = models.OneToOneField(user_models.User, on_delete=models.CASCADE, related_name='loyalty_account')
    total_points = models.PositiveIntegerField(default=0)
    lifetime_points = models.PositiveIntegerField(default=0)
    tier = models.CharField(max_length=20, choices=[
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ], default='bronze')
    
    def __str__(self):
        return f"{self.customer.username} - {self.total_points} points"

class PointTransaction(models.Model):
    account = models.ForeignKey(CustomerLoyaltyAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=[
        ('earned', 'Earned'),
        ('redeemed', 'Redeemed'),
        ('expired', 'Expired'),
    ])
    points = models.IntegerField()
    description = models.CharField(max_length=200)
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.account.customer.username} - {self.transaction_type} {self.points} points"

# Wishlist Enhancement
class WishlistItem(models.Model):
    user = models.ForeignKey(user_models.User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

# Recently Viewed Products
class RecentlyViewed(models.Model):
    user = models.ForeignKey(user_models.User, on_delete=models.CASCADE, related_name='recently_viewed')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-viewed_at']
    
    def __str__(self):
        return f"{self.user.username} viewed {self.product.name}"

# Product Comparison
class ProductComparison(models.Model):
    user = models.ForeignKey(user_models.User, on_delete=models.CASCADE, related_name='comparisons')
    products = models.ManyToManyField(Product, related_name='compared_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s comparison"

# Enhanced Notification System
class NotificationType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Notification(models.Model):
    recipient = models.ForeignKey(user_models.User, on_delete=models.CASCADE, related_name='store_notifications')
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    action_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient.username} - {self.title}"

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
    initial_total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    address = models.ForeignKey("customer.Address", on_delete=models.SET_NULL, null=True)
    coupons = models.ManyToManyField(Coupon, blank=True)
    order_id = ShortUUIDField(length=6, max_length=25, alphabet="1234567890")
    payment_id = models.CharField(null=True, blank=True, max_length=1000)
    date = models.DateTimeField(default=timezone.now)
    class Meta:
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
    initial_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    coupon = models.ManyToManyField(Coupon, blank=True)
    applied_coupon = models.BooleanField(default=False)
    item_id = ShortUUIDField(length=6, max_length=25, alphabet="1234567890")
    vendor = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, related_name="vendor_order_items")
    date = models.DateTimeField(default=timezone.now)
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


