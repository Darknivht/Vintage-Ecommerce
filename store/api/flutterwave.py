# ✅ File: store/api/flutterwave.py or store/views_flutterwave.py
# You can also place this in a general "api.py" if you prefer

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

@require_GET
@csrf_exempt  # If you're securing via frontend auth, otherwise use login_required
def get_flutterwave_banks(request, country):
    """
    Fetch list of banks for a given country from Flutterwave.
    Example country codes: NG, GH, KE, UG, ZA, TZ
    """
    url = f"https://api.flutterwave.com/v3/banks/{country}"
    headers = {
        "Authorization": f"Bearer {settings.FLUTTERWAVE_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if data.get("status") == "success":
            return JsonResponse({"banks": data.get("data", [])}, status=200)
        else:
            return JsonResponse({"error": data.get("message", "Failed to fetch banks.")}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
