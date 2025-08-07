import requests
from django.conf import settings


def create_paystack_subaccount(vendor):
    """
    Creates a Paystack subaccount for the given vendor.
    Requires: bank_name (as bank_code), account_number, store_name, and vendor email.
    Returns the subaccount_code if successful, else None.
    """
    try:
        bank_account = vendor.bankaccount

        url = "https://api.paystack.co/subaccount"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "business_name": vendor.store_name,
            "settlement_bank": bank_account.bank_name,
            "account_number": bank_account.account_number,
            "percentage_charge": 10.0,  # Platform takes 10%
            "description": f"Subaccount for {vendor.store_name}",
        }

        # Optional but good practice: fallback to user's email
        if vendor.user and vendor.user.email:
            payload["primary_contact_email"] = vendor.user.email

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if response.status_code == 200 and data.get("status") == True:
            return data["data"]["subaccount_code"]

        print("[Paystack Subaccount Error]", data.get("message"))
        return None

    except Exception as e:
        print("[Paystack Subaccount Exception]", str(e))
        return None
