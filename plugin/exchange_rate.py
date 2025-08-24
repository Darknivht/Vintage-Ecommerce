from decimal import Decimal
import requests
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Fallback exchange rates (updated periodically)
FALLBACK_RATES = {
    'INR': Decimal('83.50'),  # Approximate USD to INR rate
    'USD': Decimal('1.00'),   # USD to USD is always 1
    'NGN': Decimal('800.00'), # Approximate USD to NGN rate
}

def fetch_exchange_rates():
    """
    Fetch current exchange rates from external API with fallback handling.
    """
    try:
        # Check cache first (cache for 1 hour)
        cached_rates = cache.get('exchange_rates')
        if cached_rates:
            return cached_rates
        
        # Make API request with timeout
        response = requests.get(
            'https://api.exchangerate-api.com/v4/latest/USD',
            timeout=10  # 10 second timeout
        )
        response.raise_for_status()
        
        data = response.json()
        rates = {
            'INR': Decimal(str(data['rates'].get('INR', FALLBACK_RATES['INR']))),
            'USD': Decimal(str(data['rates'].get('USD', FALLBACK_RATES['USD']))),
            'NGN': Decimal(str(data['rates'].get('NGN', FALLBACK_RATES['NGN']))),
        }
        
        # Cache the rates for 1 hour
        cache.set('exchange_rates', rates, 3600)
        logger.info("Successfully fetched fresh exchange rates")
        return rates
        
    except Exception as e:
        logger.warning(f"Failed to fetch exchange rates: {e}. Using fallback rates.")
        # Return fallback rates if API is unavailable
        return FALLBACK_RATES.copy()

def get_exchange_rates():
    """
    Get exchange rates with lazy loading and error handling.
    """
    return fetch_exchange_rates()

def get_ngn_to_inr_rate():
    rates = get_exchange_rates()
    ngn_rate = rates['NGN']
    inr_rate = rates['INR']
    # Convert NGN to USD, then USD to INR
    return inr_rate / ngn_rate

def get_ngn_to_usd_rate():
    rates = get_exchange_rates()
    ngn_rate = rates['NGN']
    # Convert NGN to USD
    return Decimal('1.00') / ngn_rate

def convert_ngn_to_inr(ngn_amount):
    try:
        inr_rate = get_ngn_to_inr_rate()
        return Decimal(str(ngn_amount)) * inr_rate
    except Exception as e:
        logger.error(f"Error converting NGN to INR: {e}")
        # Return original amount as fallback
        return Decimal(str(ngn_amount))

def convert_ngn_to_kobo(ngn_amount):
    """
    Convert NGN to Kobo (smallest unit for payment processing).
    1 NGN = 100 Kobo
    """
    try:
        # For NGN to Kobo, we just multiply by 100
        return int(Decimal(str(ngn_amount)) * 100)
    except Exception as e:
        logger.error(f"Error converting NGN to Kobo: {e}")
        return int(float(ngn_amount) * 100)

def convert_ngn_to_usd(ngn_amount):
    try:
        usd_rate = get_ngn_to_usd_rate()
        return Decimal(str(ngn_amount)) * usd_rate
    except Exception as e:
        logger.error(f"Error converting NGN to USD: {e}")
        # Return a reasonable fallback (using fallback rate)
        return Decimal(str(ngn_amount)) / FALLBACK_RATES['NGN']

