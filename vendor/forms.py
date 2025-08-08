import requests
from django import forms
from django.conf import settings
from vendor.models import BankAccount


class BankAccountForm(forms.ModelForm):
    bank_name = forms.ChoiceField(choices=[], required=True, label="Bank")
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
        # Use the proven fetch method
        self.fields["bank_name"].choices = self.get_nigerian_banks()
        self.fields["bank_name"].widget.attrs.update({
            "class": "form-control",
            "id": "id_bank_name",
            "name": "bank_name"
        })

    def get_nigerian_banks(self):
        """
        Fetch Nigerian bank list from Paystack (default behavior).
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
        return [("", "No banks available")]
