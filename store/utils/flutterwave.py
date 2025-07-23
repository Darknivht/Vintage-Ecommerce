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
    Initiates a Flutterwave payment with multiple subaccount splits.
    Each subaccount dict must include:
        {
            "id": str,  # subaccount ID
            "transaction_charge_type": "percentage",
            "transaction_charge": float  # e.g. 90.0 for 90%
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


def calculate_vendor_flat_splits(order: Order, platform_share_percent=10):
    """
    Calculates vendor payouts using flat amounts.
    Returns a list of Flutterwave-compatible subaccounts:
    [
        {"id": "RS_XXX", "transaction_charge_type": "flat", "transaction_charge": 1350.00},
        ...
    ]
    """
    subaccount_amounts = {}

    for item in order.order_items():
        vendor = item.vendor

        if not vendor:
            continue

        try:
            bank_account = vendor.vendor.bankaccount
            subaccount_id = bank_account.flutterwave_subaccount_id
            if not subaccount_id:
                continue

            vendor_percent = 100 - platform_share_percent
            vendor_amount = float(item.sub_total) * (vendor_percent / 100)

            if subaccount_id in subaccount_amounts:
                subaccount_amounts[subaccount_id] += vendor_amount
            else:
                subaccount_amounts[subaccount_id] = vendor_amount

        except Exception as e:
            print(f"Skipping vendor {vendor} due to: {e}")
            continue

    return [
        {
            "id": sub_id,
            "transaction_charge_type": "flat",
            "transaction_charge": round(amount, 2)
        }
        for sub_id, amount in subaccount_amounts.items()
    ]