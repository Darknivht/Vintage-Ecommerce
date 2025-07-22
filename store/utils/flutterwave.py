import requests
from django.conf import settings
from store.models import Order

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


def initiate_flutterwave_payment(amount, currency, tx_ref, customer, redirect_url, subaccounts):
    """
    Initiates a Flutterwave payment with vendor/platform splits.
    
    Each subaccount dict must include:
        {
            "id": str,  # subaccount ID
            "transaction_split_ratio": float  # e.g. 25.50 for 25.5%
        }
    """
    url = "https://api.flutterwave.com/v3/payments"
    headers = {
        "Authorization": f"Bearer {FLW_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "tx_ref": tx_ref,
        "amount": float(amount),
        "currency": currency,
        "redirect_url": redirect_url,
        "payment_options": "card,banktransfer,ussd",
        "customer": customer,
        "customizations": {
            "title": "Vintage Store Payment",
            "description": f"Order split for {len(subaccounts)} vendors",
        },
        "subaccounts": subaccounts
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if data.get("status") == "success":
            return data["data"]
        else:
            raise Exception(f"Flutterwave Payment Error: {data.get('message')} | Payload: {payload}")

    except requests.RequestException as e:
        raise Exception(f"Payment request failed: {str(e)}")
