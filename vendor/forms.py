from django import forms
from vendor.models import BankAccount
import requests
from django.conf import settings

class BankAccountForm(forms.ModelForm):
    bank_name = forms.ChoiceField(choices=[], required=True, label="Bank Name")
    account_name = forms.CharField(required=False, label="Business Name (optional)")

    class Meta:
        model = BankAccount
        fields = ['bank_name', 'account_number', 'account_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bank_name'].choices = self.get_nigerian_banks()
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def get_nigerian_banks(self):
        url = "https://api.paystack.co/bank?country=ng"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                banks = r.json().get("data", [])
                return [(b["code"], b["name"]) for b in banks]
        except Exception as e:
            print("Bank fetch error:", e)
        return [('', 'No banks available')]
