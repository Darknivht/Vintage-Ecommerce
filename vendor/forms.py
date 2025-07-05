import requests
from django import forms
from vendor.models import BankAccount
from django.conf import settings


class BankAccountForm(forms.ModelForm):
    bank_name = forms.ChoiceField(choices=[], required=True, label="Bank Name")

    class Meta:
        model = BankAccount
        fields = [
            "account_type", "country", "currency", "bank_name", "bank_code", "branch_code",
            "account_number", "account_name", "email", "split_value", "paypal_address"
        ]

    def __init__(self, *args, **kwargs):
        super(BankAccountForm, self).__init__(*args, **kwargs)

        self.fields['country'].widget.attrs.update({'class': 'form-control'})
        self.fields['bank_name'].widget.attrs.update({'class': 'form-control'})

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        # Detect selected country (either from initial or POST data)
        country = self.initial.get('country') or self.data.get('country') or 'NG'
        self.fields['bank_name'].choices = self.get_banks_by_country(country)

    def get_banks_by_country(self, country_code):
        """
        Fetch banks from Flutterwave API based on selected country.
        Returns a list of (code, name) tuples.
        """
        url = f"https://api.flutterwave.com/v3/banks/{country_code}"
        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_PRIVATE_KEY}",
            "Content-Type": "application/json"
        }

        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                banks = res.json().get('data', [])
                return [(bank['code'], bank['name']) for bank in banks]
        except Exception as e:
            print(f"[Flutterwave Bank Fetch Error] {e}")

        return [('', 'No banks available')]
