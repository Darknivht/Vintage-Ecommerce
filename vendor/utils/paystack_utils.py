import requests
from django.conf import settings

PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
BASE_URL = "https://api.paystack.co"


def get_headers():
    return {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def create_paystack_customer(email, full_name):
    url = f"{BASE_URL}/customer"
    payload = {
        "email": email,
        "first_name": full_name.split()[0],
        "last_name": " ".join(full_name.split()[1:]) or full_name.split()[0],
    }
    response = requests.post(url, json=payload, headers=get_headers())
    data = response.json()
    if data.get("status"):
        return data["data"]
    else:
        raise Exception(f"Paystack customer creation failed: {data.get('message')}")


def create_dedicated_virtual_account(customer_code, preferred_bank=None):
    url = f"{BASE_URL}/dedicated_account"
    payload = {
        "customer": customer_code
    }
    if preferred_bank:
        payload["preferred_bank"] = preferred_bank  # e.g., "wema-bank"

    response = requests.post(url, json=payload, headers=get_headers())
    data = response.json()
    if data.get("status"):
        return data["data"]
    else:
        raise Exception(f"Virtual account creation failed: {data.get('message')}")


def create_transfer_recipient(account_name, account_number, bank_code):
    url = f"{BASE_URL}/transferrecipient"
    payload = {
        "type": "nuban",
        "name": account_name,
        "account_number": account_number,
        "bank_code": bank_code,
        "currency": "NGN"
    }
    response = requests.post(url, json=payload, headers=get_headers())
    data = response.json()
    if data.get("status"):
        return data["data"]
    else:
        raise Exception(f"Transfer recipient creation failed: {data.get('message')}")


def initiate_transfer(amount, recipient_code, reason="Vendor Withdrawal"):
    url = f"{BASE_URL}/transfer"
    payload = {
        "source": "balance",
        "amount": int(amount * 100),  # Paystack expects kobo
        "recipient": recipient_code,
        "reason": reason
    }
    response = requests.post(url, json=payload, headers=get_headers())
    data = response.json()
    if data.get("status"):
        return data["data"]
    else:
        raise Exception(f"Transfer failed: {data.get('message')}")


def get_paystack_bank_list():
    url = f"{BASE_URL}/bank"
    response = requests.get(url, headers=get_headers())
    data = response.json()
    if data.get("status"):
        return data["data"]
    else:
        return []


def transfer_to_bank_account(vendor, amount):
    """
    Transfers money to a vendor's bank account using Paystack.
    - Creates a transfer recipient if needed.
    - Sends money to vendor via Paystack.
    """
    from vendor.models import BankAccount

    account = BankAccount.objects.get(vendor=vendor)

    if not account or not account.account_number or not account.bank_code:
        raise Exception("Vendor bank account is incomplete.")

    # ✅ Step 1: Create transfer recipient (if not already saved)
    if not hasattr(account, 'paystack_recipient_code') or not account.paystack_recipient_code:
        recipient_payload = {
            "type": "nuban",
            "name": account.account_name,
            "account_number": account.account_number,
            "bank_code": account.bank_code,
            "currency": "NGN",
        }

        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            f"{BASE_URL}/transferrecipient", json=recipient_payload, headers=headers
        )
        data = response.json()

        if not data.get("status"):
            raise Exception(f"Failed to create recipient: {data.get('message')}")

        recipient_code = data["data"]["recipient_code"]
        account.paystack_recipient_code = recipient_code
        account.save()
    else:
        recipient_code = account.paystack_recipient_code

    # ✅ Step 2: Initiate transfer
    transfer_payload = {
        "source": "balance",
        "amount": int(float(amount) * 100),  # Convert Naira to Kobo
        "recipient": recipient_code,
        "reason": f"Payout to {vendor.store_name}",
    }

    response = requests.post(
        f"{BASE_URL}/transfer", json=transfer_payload, headers={
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
    )

    data = response.json()

    if not data.get("status"):
        raise Exception(f"Transfer failed: {data.get('message')}")

    return data["data"]
