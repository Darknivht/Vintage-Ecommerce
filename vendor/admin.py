from django.contrib import admin
from .models import Vendor, BankAccount, Payout, Notifications


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("store_name", "user", "subaccount_code", "country", "date")
    readonly_fields = ("subaccount_code", "slug")
    search_fields = ("store_name", "user__email")
    list_filter = ("country", "date")
    ordering = ("-date",)

    fieldsets = (
        (None, {
            "fields": ("user", "store_name", "slug", "description", "image", "country")
        }),
        ("Paystack", {
            "fields": ("subaccount_code",),
            "description": "This is the Paystack subaccount code used for split payments."
        }),
    )


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("vendor", "bank_name", "account_number", "subaccount_code", "created_at")
    search_fields = ("vendor__store_name", "account_number", "subaccount_code")
    list_filter = ("bank_name", "created_at")



@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ("vendor", "amount", "item", "date")
    search_fields = ("vendor__store_name",)
    list_filter = ("date",)


@admin.register(Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "order", "seen", "date")
    list_filter = ("type", "seen", "date")
