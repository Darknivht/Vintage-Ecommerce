import requests
from django.conf import settings

PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY

def create_paystack_subaccount(vendor):
    """
    Creates a Paystack subaccount for the vendor and returns the subaccount_code.
    """
    url = "https://api.paystack.co/subaccount"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        bank = vendor.bankaccount
        business_name = bank.account_name or vendor.store_name  # fallback logic
        payload = {
            "business_name": business_name,
            "settlement_bank": bank.bank_code,         # Must be actual bank code like "058"
            "account_number": bank.account_number,
            "percentage_charge": 10                    # Platform takes 10%
        }

        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()

        if response.status_code != 200 or res_data.get("status") != True:
            raise Exception(f"[Paystack Error] {res_data.get('message')} | Payload: {payload}")

        return res_data["data"]["subaccount_code"]

    except Exception as e:
        print("[Subaccount Creation Failed]", e)
        return None
