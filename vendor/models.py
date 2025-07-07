from django.db import models
from shortuuid.django_fields import ShortUUIDField
from userauths.models import User
from django.utils.text import slugify
from django.conf import settings
import requests
from cloudinary.models import CloudinaryField

# Helper: Get supported countries for dropdown
def get_supported_flutterwave_countries():
    return [
        ("NG", "Nigeria"),
        ("GH", "Ghana"),
        ("CI", "Côte d'Ivoire"),
        ("SN", "Senegal"),
        ("BJ", "Benin"),
        ("TG", "Togo"),
        ("GM", "Gambia"),
        ("GN", "Guinea"),
        ("LR", "Liberia"),
        ("SL", "Sierra Leone"),
        ("GLOBAL", "Other / Global"),
    ]

# Helper: Map country to currency
CURRENCY_MAP = {
    "NG": "NGN",
    "GH": "GHS",
    "CI": "XOF",
    "SN": "XOF",
    "BJ": "XOF",
    "TG": "XOF",
    "GM": "GMD",
    "GN": "GNF",
    "LR": "LRD",
    "SL": "SLL",
    "GLOBAL": "USD",
}

# Fetch Flutterwave bank list per country
def get_flutterwave_banks(country_code):
    try:
        url = f"https://api.flutterwave.com/v3/banks/{country_code}"
        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_PRIVATE_KEY}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        banks = response.json().get("data", [])
        return [(bank["code"], bank["name"]) for bank in banks]
    except Exception as e:
        print("Flutterwave bank fetch error:", e)
        return []

# Create subaccount via Flutterwave API
def create_flutterwave_subaccount(data):
    try:
        url = "https://api.flutterwave.com/v3/subaccounts"
        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_PRIVATE_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json().get("data", {}).get("id", None)
    except Exception as e:
        print("Flutterwave subaccount creation error:", e)
        return None

# ====================== MODELS ==========================

NOTIFICATION_TYPE = (
    ("New Order", "New Order"),
    ("New Review", "New Review"),
)

PAYOUT_METHOD = (
    ("PayPal", "PayPal"),
    ("Stripe", "Stripe"),
    ("Nigerian Bank Account", "Nigerian Bank Account"),
    ("Indian Bank Account", "Indian Bank Account"),
    ("USA Bank Account", "USA Bank Account"),
)

NOTIFICATION_EVENT = (
    ("New Order", "New Order"),
    ("Item Shipped", "Item Shipped"),
    ("Item Delivered", "Item Delivered"),
)

class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name="vendor")
    image = CloudinaryField(folder="images", blank=True)
    store_name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    vendor_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(blank=True, null=True)

    def __str__(self):
        return str(self.store_name)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.store_name)
        super().save(*args, **kwargs)

class BankAccount(models.Model):
    vendor = models.OneToOneField(Vendor, on_delete=models.SET_NULL, null=True)
    account_type = models.CharField(max_length=50, choices=PAYOUT_METHOD, null=True, blank=True)

    country = models.CharField(
        max_length=16,
        choices=get_supported_flutterwave_countries(),
        default="NG",
        help_text="Vendor’s country for bank account verification"
    )

    currency = models.CharField(max_length=10, blank=True, null=True)
    bank_name = models.CharField(max_length=255)
    bank_code = models.CharField(max_length=50, null=True, blank=True)
    branch_code = models.CharField(max_length=50, null=True, blank=True)
    account_number = models.CharField(max_length=50)
    account_name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)

    flutterwave_subaccount_id = models.CharField(max_length=100, null=True, blank=True)
    split_value = models.PositiveIntegerField(default=1, null=True, blank=True)

    stripe_id = models.CharField(max_length=100, null=True, blank=True)
    paypal_address = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Bank Accounts"

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"

    def has_subaccount(self):
        return bool(self.flutterwave_subaccount_id)

    def save(self, *args, **kwargs):
        # Auto fill currency
        if self.country and not self.currency:
            self.currency = CURRENCY_MAP.get(self.country, "USD")

        # Fetch bank_code based on name
        if self.country and self.bank_name and not self.bank_code:
            banks = get_flutterwave_banks(self.country)
            for code, name in banks:
                if name.lower() == self.bank_name.lower():
                    self.bank_code = code
                    break

        # Create subaccount if missing
        if not self.flutterwave_subaccount_id and self.account_number and self.bank_code:
            if self.vendor and self.vendor.store_name and self.email:
                payload = {
                    "account_bank": self.bank_code,
                    "account_number": self.account_number,
                    "business_name": self.vendor.store_name,
                    "business_email": self.email,
                    "business_contact": {
                        "name": self.account_name,
                        "email": self.email
                    },
                    "split_type": "percentage",
                    "split_value": self.split_value or 1
                }
                subaccount_id = create_flutterwave_subaccount(payload)
                if subaccount_id:
                    self.flutterwave_subaccount_id = subaccount_id

        super().save(*args, **kwargs)

class Payout(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey("store.OrderItem", on_delete=models.SET_NULL, null=True, related_name="item")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payout_id = ShortUUIDField(unique=True, length=6, max_length=10, alphabet="1234567890")
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Payout to {self.vendor} - ₦{self.amount}"

    class Meta:
        ordering = ['-date']

class Notifications(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="vendor_notifications")
    type = models.CharField(max_length=100, choices=NOTIFICATION_EVENT, default="New Order")
    order = models.ForeignKey("store.OrderItem", on_delete=models.CASCADE, null=True, blank=True)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.user} - {self.type}"
