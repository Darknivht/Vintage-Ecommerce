from django.db import models
from shortuuid.django_fields import ShortUUIDField
from userauths.models import User
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
from vendor.utils.paystack import create_paystack_subaccount


NOTIFICATION_EVENT = (
    ("New Order", "New Order"),
    ("Item Shipped", "Item Shipped"),
    ("Item Delivered", "Item Delivered"),
)


class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="vendor")
    store_name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, null=True)
    image = CloudinaryField(folder="vendors", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, default="NG")

    # 🔐 Paystack Banking Info
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    bank_code = models.CharField(max_length=10, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    account_name = models.CharField(max_length=255, blank=True, null=True)
    subaccount_code = models.CharField(max_length=255, blank=True, null=True, help_text="Generated from Paystack")

    vendor_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.store_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.store_name



class BankAccount(models.Model):
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name="bankaccount")
    bank_name = models.CharField(max_length=255)
    bank_code = models.CharField(max_length=10, help_text="e.g. '058' for GTBank")
    account_number = models.CharField(max_length=50)
    account_name = models.CharField(max_length=255, null=True, blank=True)  # Optional

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"



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