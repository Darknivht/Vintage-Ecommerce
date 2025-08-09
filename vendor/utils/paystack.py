import requests
from django.conf import settings

def create_paystack_subaccount(vendor, bank_code, account_number, account_name=None):
    """
    Create a Paystack subaccount and return the subaccount code.
    """
    url = "https://api.paystack.co/subaccount"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "business_name": account_name or vendor.store_name,
        "settlement_bank": bank_code,
        "account_number": account_number,
        "percentage_charge": 10.0,  # Platform keeps 10%, vendor gets 90%
        "primary_contact_email": vendor.user.email,
        "settlement_schedule": "auto"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        print("[Paystack Response]", data)

        if response.status_code == 200 and data.get("status") is True:
            subaccount_code = data["data"].get("subaccount_code")
            print("[Subaccount Created] Code:", subaccount_code)
            return subaccount_code
        else:
            print("[Paystack Subaccount Error]", data.get("message"))
            return None
    except Exception as e:
        print("[Paystack Exception]", str(e))
        return None


def fetch_paystack_subaccount_details(subaccount_code):
    """
    Fetch details of an existing Paystack subaccount.
    """
    url = f"https://api.paystack.co/subaccount/{subaccount_code}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        print("[Fetch Subaccount Response]", data)

        if response.status_code == 200 and data.get("status") is True:
            return data.get("data")
        else:
            print("[Fetch Subaccount Error]", data.get("message"))
            return None
    except Exception as e:
        print("[Fetch Subaccount Exception]", str(e))
        return None
