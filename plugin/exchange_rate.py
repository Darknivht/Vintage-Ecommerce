from decimal import Decimal
import requests

def fetch_exchange_rates():
    response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
    data = response.json()
    return {
        'INR': Decimal(data['rates']['INR']),
        'USD': Decimal(data['rates']['USD'])
    }

exchange_rates = fetch_exchange_rates()

def get_ngn_to_inr_rate():
    return exchange_rates['INR']

def get_ngn_to_usd_rate():
    return exchange_rates['USD']

def convert_ngn_to_inr(ngn_amount):
    inr_rate = get_ngn_to_inr_rate()
    return ngn_amount * inr_rate

def convert_ngn_to_kobo(ngn_amount):
    usd_rate = get_ngn_to_usd_rate()
    usd_amount = ngn_amount * usd_rate
    return int(usd_amount * 100)  # Convert NGN to Kobo

def convert_ngn_to_usd(ngn_amount):
    usd_rate = get_ngn_to_usd_rate()
    return ngn_amount * usd_rate

