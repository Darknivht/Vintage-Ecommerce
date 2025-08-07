import requests
from django.conf import settings


# vendor/utils/paystack.py

def create_paystack_subaccount(vendor):
    from vendor.models import BankAccount

    try:
        bank = vendor.bankaccount
    except BankAccount.DoesNotExist:
        return None

    url = "https://api.paystack.co/subaccount"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    # Use custom name if provided, else vendor.store_name
    business_name = bank.account_name

    payload = {
        "business_name": business_name,
        "settlement_bank": bank.bank_name,  # bank name may need to be code (e.g., "058")
        "account_number": bank.account_number,
        "percentage_charge": 10  # platform cut
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if response.status_code == 200 and data["status"] == True:
            return data["data"]["subaccount_code"]
        else:
            print("[Paystack Error]", data.get("message"))
            return None
    except Exception as e:
        print("[Paystack Exception]", str(e))
        return None
