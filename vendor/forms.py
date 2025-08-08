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
            "class": "form-control"
        })
    )

    class Meta:
        model = BankAccount
        fields = ["account_name", "account_number", "bank_name", "bank_code"]
        widgets = {
            "account_number": forms.TextInput(attrs={
                "placeholder": "e.g., 0123456789",
                "class": "form-control"
            }),
            "bank_code": forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["bank_name"].choices = self.get_nigerian_banks()
        self.fields["bank_name"].widget.attrs.update({"class": "form-control"})

    def get_nigerian_banks(self):
        """
        Fetch Nigerian bank list from Paystack.
        """
        url = "https://api.paystack.co/bank"  # No ?country=ng for compatibility
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                banks = response.json().get("data", [])
                # Filter for Nigerian banks
                nigeria_banks = [
                    (bank["code"], bank["name"])
                    for bank in banks if bank.get("country") == "Nigeria"
                ]
                return nigeria_banks if nigeria_banks else [("", "No banks available")]
        except Exception as e:
            print("[Bank Fetch Error]", e)
        return [("", "No banks available")]
