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
        self.fields['bank_name'].choices = self.get_banks_by_country(country)

        # Style all fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def get_banks_by_country(self, country_code):
        """
        Fetch banks from Paystack API based on selected country.
        Returns list of (bank_code, bank_name) tuples.
        """
        url = f"https://api.paystack.co/bank?country={country_code}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                banks = res.json().get('data', [])
                return [(bank['code'], bank['name']) for bank in banks]
        except Exception as e:
            print(f"[Bank Fetch Error]: {e}")

        return [('', 'No banks available')]
