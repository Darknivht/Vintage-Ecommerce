from django.contrib import admin
from userauths import models as userauths_models
from django.contrib import admin
from vendor.models import BankAccount
from vendor.forms import BankAccountForm



class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name']

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'subject', 'date']



class BankAccountAdmin(admin.ModelAdmin):
    form = BankAccountForm
    list_display = ['vendor', 'account_number', 'country', 'bank_name', 'flutterwave_subaccount_id']


admin.site.register(userauths_models.User, UserAdmin)
admin.site.register(userauths_models.Profile, ProfileAdmin)
admin.site.register(userauths_models.ContactMessage, ContactMessageAdmin)
    