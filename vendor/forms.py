from django import forms
from .models import BankAccount

class BankAccountForm(forms.ModelForm):
    bank_name = forms.ChoiceField(
        choices=[],
        required=True,
        label="Bank",
        widget=forms.Select(attrs={
            "class": "form-control",
        })
    )

    class Meta:
        model = BankAccount
        fields = ["bank_name", "account_number", "account_name"]
        widgets = {
            "account_number": forms.TextInput(attrs={
                "placeholder": "e.g., 0123456789",
                "class": "form-control",
            }),
            "account_name": forms.TextInput(attrs={
                "placeholder": "Optional",
                "class": "form-control",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["bank_name"].choices = self.get_nigerian_banks()

    def get_nigerian_banks(self):
        """Fetch Nigerian bank list from Paystack."""
        url = "https://api.paystack.co/bank"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            banks = response.json().get("data", [])
            return [(bank["code"], bank["name"]) for bank")
        except requests.RequestException as e:
            print("[Bank Fetch Error]", e)
            return [("", "No banks available")]