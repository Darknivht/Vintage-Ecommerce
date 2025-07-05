import requests
from django.conf import settings

FLW_SECRET_KEY = settings.FLUTTERWAVE_PRIVATE_KEY

def create_flutterwave_subaccount(
    account_name, account_number, bank_code,
    vendor_email, country, currency, split_value,
    split_type="percentage"
):
    """
    Create a Flutterwave subaccount and return subaccount_id.
    Raises exception with detailed info on failure.
    """
    url = "https://api.flutterwave.com/v3/subaccounts"
    headers = {
        "Authorization": f"Bearer {FLW_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "account_bank": bank_code,
        "account_number": account_number,
        "business_name": account_name,
        "business_email": vendor_email,
        "split_type": split_type,
        "split_value": float(split_value),
        "country": country,
        "currency": currency,
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if response.status_code != 200 or data.get("status") != "success":
            raise Exception(f"Flutterwave Error: {data.get('message')} | Payload: {payload}")

        return data["data"]["subaccount_id"]

    except requests.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")
