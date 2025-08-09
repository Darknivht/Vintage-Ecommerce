import requests
from django import forms
from django.conf import settings
from vendor.models import BankAccount


class BankAccountForm(forms.ModelForm):
    bank_name = forms.ChoiceField(
        choices=[("", "Select Bank")],  # Default placeholder
        required=True,
        label="Bank",
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "id_bank_name",
            "name": "bank_name"
        })
    )

    account_name = forms.CharField(
        required=False,
        label="Account Name (Optional)",
        widget=forms.TextInput(attrs={
            "placeholder": "Optional – will use store name if empty",
            "class": "form-control",
            "id": "id_account_name",
            "name": "account_name"
        })
    )

    class Meta:
        model = BankAccount
        fields = ["account_name", "account_number", "bank_name", "bank_code"]

        widgets = {
            "account_number": forms.TextInput(attrs={
                "placeholder": "e.g., 0123456789",
                "class": "form-control",
                "id": "id_account_number",
                "name": "account_number"
            }),
            "bank_code": forms.HiddenInput(attrs={
                "id": "id_bank_code",
                "name": "bank_code"
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate bank list from Paystack
        banks = self.get_nigerian_banks()
        if banks:
            self.fields["bank_name"].choices += banks  # Append to placeholder

    def get_nigerian_banks(self):
        """
        Fetch Nigerian bank list from Paystack API.
        """
        url = "https://api.paystack.co/bankn"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                banks = response.json().get("data", [])
                return [(bank["code"], bank["name"]) for bank in banks if bank.get("code") and bank.get("name")]
        except Exception as e:
            print("[Bank Fetch Error]", e)
        return []
