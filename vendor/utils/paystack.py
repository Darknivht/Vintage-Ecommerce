import requests
from django.conf import settings

def create_paystack_subaccount(vendor_data):
    """Create a Paystack subaccount and return the subaccount code."""
    url = "https://api.paystack.co/subaccount"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    try:
        response = requests.post(url, headers=headers, json=vendor_data)
        response.raise_for_status()
        data = response.json()
        print("[Paystack Response]", data)
        if data.get("status") is True:
            subaccount_code = data["data"].get("subaccount_code")
            print("[Subaccount Created] Code:", subaccount_code)
            return subaccount_code
        else:
            print("[Paystack Subaccount Error]", data.get("message"))
            return None
    except requests.exceptions.RequestException as e:
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
