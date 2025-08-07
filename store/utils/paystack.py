# store/utils/paystack.py

import requests
from django.conf import settings

PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
PAYSTACK_BASE_URL = "https://api.paystack.co"


def initialize_paystack_transaction(email, amount_in_kobo, split_data, callback_url, reference):
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "email": email,
        "amount": amount_in_kobo,
        "reference": reference,
        "callback_url": callback_url,
        "split": split_data,
    }

    response = requests.post(f"{PAYSTACK_BASE_URL}/transaction/initialize", json=payload, headers=headers)
    data = response.json()

    if response.status_code != 200 or not data.get("status"):
        raise Exception(f"Paystack Error: {data.get('message')}")

    return data["data"]  # contains 'authorization_url' and 'reference'
