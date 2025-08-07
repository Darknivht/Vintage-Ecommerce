import requests
from django import forms
from django.conf import settings
from vendor.models import BankAccount


class BankAccountForm(forms.ModelForm):
    bank_name = forms.ChoiceField(choices=[], required=True, label="Bank Name")
    account_name = forms.CharField(required=False, label="Account Name (optional)")

    class Meta:
        model = BankAccount
        fields = ['bank_name', 'account_number', 'account_name']

    def __init__(self, *args, **kwargs):
        super(BankAccountForm, self).__init__(*args, **kwargs)

        # Detect selected country for bank list, default to NG (Nigeria)
        country = self.initial.get('country') or self.data.get('country') or 'NG'
        self.fields['bank_name'].choices = self.get_nigerian_banks(country)

        # Style all fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def get_nigerian_banks(self):
        """
        Fetches bank list from Paystack.
        """
        url = "https://api.paystack.co/bank"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                banks = response.json().get("data", [])
                return [(bank["code"], bank["name"]) for bank in banks]
        except Exception as e:
            print("[Bank Fetch Error]", e)

        return [('', 'No banks available')]