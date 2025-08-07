
def create_paystack_subaccount(vendor, bank_name, bank_code, account_number, account_name=None):
    """
    Creates a Paystack subaccount for vendor using their bank details.
    """
    url = "https://api.paystack.co/subaccount"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "business_name": account_name,
        "settlement_bank": bank_code,
        "account_number": account_number,
        "percentage_charge": 10  # Platform keeps 10%, vendor gets 90%
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if response.status_code == 200 and data.get("status") is True:
            return data["data"]["subaccount_code"]
        else:
            print("[Paystack Subaccount Error]", data.get("message"))
            return None
    except Exception as e:
        print("[Paystack Exception]", e)
        return None