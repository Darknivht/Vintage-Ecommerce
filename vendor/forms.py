import requests
from django import forms
from django.conf import settings
from vendor.models import BankAccount


class BankAccountForm(forms.ModelForm):
    bank_name = forms.ChoiceField(choices=[], required=True, label="Bank Name")
    account_name = forms.CharField(required=False, label="Business Name (optional)")

    class Meta:
        model = BankAccount
        fields = ['bank_name', 'account_number', 'account_name']

    def __init__(self, *args, **kwargs):
        super(BankAccountForm, self).__init__(*args, **kwargs)

        # Only support Nigeria — hardcoded bank list fetch
        self.fields['bank_name'].choices = self.get_nigerian_banks()

        # Style all fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def get_nigerian_banks(self):
        """
        Fetch bank list from Paystack — Nigeria only.
        """
        url = "https://api.paystack.co/bank?country=nigeria"
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
            print("[Paystack Bank Fetch Error]", e)

        return [('', 'No banks available')]
