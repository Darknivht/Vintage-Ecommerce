# store/utils/paystack.py

import requests
from django.conf import settings
from decimal import Decimal
from collections import defaultdict

PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
PAYSTACK_BASE_URL = "https://api.paystack.co"


def initialize_paystack_transaction(email, amount_in_kobo, split_data, callback_url, reference):
    """Initialize a Paystack transaction with split payment support"""
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "email": email,
        "amount": amount_in_kobo,
        "callback_url": callback_url,
        "reference": reference
    }
    
    # Only add split data if it exists and has subaccounts
    if split_data and split_data.get("subaccounts"):
        data["split"] = split_data
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()


def verify_paystack_transaction(reference):
    """Verify a Paystack transaction"""
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        print(f"[Paystack Verify Error] {e}")
        return {"status": False, "message": str(e)}


def calculate_marketplace_split(order):
    """
    Calculate split payment for marketplace with multiple vendors
    Returns split data for Paystack and vendor breakdown
    """
    from store.models import OrderItem
    
    # Group order items by vendor
    vendor_totals = defaultdict(Decimal)
    vendor_subaccounts = {}
    
    for item in order.order_items():
        vendor = item.vendor
        item_total = Decimal(str(item.total))  # Include shipping in total
        vendor_totals[vendor] += item_total
        
        # Get vendor subaccount code
        try:
            if hasattr(vendor, 'vendor') and vendor.vendor.subaccount_code:
                vendor_subaccounts[vendor] = vendor.vendor.subaccount_code
            else:
                print(f"[Split Warning] Vendor {vendor} has no subaccount code")
                vendor_subaccounts[vendor] = None
        except Exception as e:
            print(f"[Split Error] Error getting subaccount for {vendor}: {e}")
            vendor_subaccounts[vendor] = None
    
    # Calculate splits
    subaccounts = []
    total_amount = Decimal(str(order.total))
    platform_fee_total = Decimal('0')
    
    for vendor, vendor_total in vendor_totals.items():
        subaccount_code = vendor_subaccounts.get(vendor)
        
        if subaccount_code:
            # Calculate vendor share (90% of their items total)
            vendor_share = vendor_total * Decimal('0.90')
            platform_fee = vendor_total * Decimal('0.10')
            platform_fee_total += platform_fee
            
            # Convert to kobo (Paystack uses kobo)
            vendor_share_kobo = int(vendor_share * 100)
            
            subaccounts.append({
                "subaccount": subaccount_code,
                "share": vendor_share_kobo,
            })
            
            print(f"[Split] Vendor {vendor}: ₦{vendor_total} -> Vendor gets ₦{vendor_share}, Platform gets ₦{platform_fee}")
        else:
            print(f"[Split Skip] Vendor {vendor} has no subaccount - amount ₦{vendor_total} goes to platform")
    
    # Create split data
    split_data = None
    if subaccounts:
        split_data = {
            "type": "flat",
            "currency": "NGN",
            "subaccounts": subaccounts,
            "bearer_type": "subaccount"
        }
    
    return {
        "split_data": split_data,
        "vendor_count": len(vendor_totals),
        "vendors_with_subaccounts": len(subaccounts),
        "platform_fee_total": platform_fee_total,
        "subaccounts": subaccounts
    }


def create_paystack_split_payment(order, callback_url):
    """
    Create a Paystack payment with marketplace split logic
    """
    # Calculate marketplace split
    split_info = calculate_marketplace_split(order)
    
    amount_in_kobo = int(Decimal(str(order.total)) * 100)
    reference = f"ORDER-{order.order_id}"
    
    # Initialize transaction
    try:
        paystack_response = initialize_paystack_transaction(
            email=order.address.email,
            amount_in_kobo=amount_in_kobo,
            split_data=split_info["split_data"],
            callback_url=callback_url,
            reference=reference
        )
        
        if paystack_response.get("status"):
            return {
                "success": True,
                "authorization_url": paystack_response["data"]["authorization_url"],
                "reference": reference,
                "split_info": split_info
            }
        else:
            return {
                "success": False,
                "error": paystack_response.get("message", "Unknown error"),
                "split_info": split_info
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "split_info": split_info
        }
