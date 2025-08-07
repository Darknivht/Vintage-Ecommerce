import requests
from django import forms
from django.conf import settings
from vendor.models import Vendor

class BankAccountForm(forms.ModelForm):
    bank_name = forms.ChoiceField(choices=[], required=True, label="Bank")
    account_name = forms.CharField(required=False, label="Account Name (Optional)")

    class Meta:
        model = Vendor
        fields = ["account_name", "account_number", "bank_name", "bank_code"]

        widgets = {
            "account_number": forms.TextInput(attrs={"placeholder": "e.g., 0123456789"}),
            "bank_code": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(BankAccountForm, self).__init__(*args, **kwargs)

        self.fields["bank_name"].choices = self.get_nigerian_banks()
        self.fields["bank_name"].widget.attrs.update({"class": "form-control"})
        self.fields["account_name"].widget.attrs.update({"class": "form-control", "placeholder": "Optional – will use store name if empty"})
        self.fields["account_number"].widget.attrs.update({"class": "form-control"})

    def get_nigerian_banks(self):
        """
        Fetch Nigerian bank list from Paystack.
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
