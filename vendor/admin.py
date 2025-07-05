from django.contrib import admin
from vendor import models as vendor_models


class VendorAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'user', 'country', 'vendor_id', 'date']
    search_fields = ['store_name', 'user__username', 'vendor_id']
    prepopulated_fields = {'slug': ('store_name',)}
    list_filter = ['country', 'date']
    readonly_fields = ['vendor_id', 'slug']


class BankAccountAdmin(admin.ModelAdmin):
    list_display = [
        'vendor', 'country', 'currency', 'bank_name',
        'account_number', 'account_type',
        'flutterwave_subaccount_id', 'split_value'
    ]
    search_fields = ['vendor__store_name', 'bank_name', 'account_number', 'flutterwave_subaccount_id']
    list_filter = ['account_type', 'country', 'flutterwave_subaccount_id']
    list_editable = ['split_value']
    readonly_fields = ['flutterwave_subaccount_id', 'bank_code', 'currency']

    def save_model(self, request, obj, form, change):
        obj.save()


class PayoutAdmin(admin.ModelAdmin):
    list_display = ['payout_id', 'vendor', 'item', 'amount', 'date']
    search_fields = ['payout_id', 'vendor__store_name', 'item__order__order_id']
    list_filter = ['date', 'vendor']
    readonly_fields = ['payout_id', 'date']


class NotificationsAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'order', 'seen', 'date']
    list_editable = ['order', 'seen']
    list_filter = ['type', 'seen', 'date']


# ✅ Register models once only
admin.site.register(vendor_models.Vendor, VendorAdmin)
admin.site.register(vendor_models.BankAccount, BankAccountAdmin)
admin.site.register(vendor_models.Payout, PayoutAdmin)
admin.site.register(vendor_models.Notifications, NotificationsAdmin)
