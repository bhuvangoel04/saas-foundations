from django.template.defaultfilters import default
import razorpay
from decouple import config
from datetime import datetime
import helpers.date_utils as date_utils

DJANGO_DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)
RAZORPAY_SECRET_KEY = config("RAZORPAY_SECRET_KEY", default="", cast=str)
RAZORPAY_KEY_ID = config("RAZORPAY_KEY_ID")

if "rzp_test" in RAZORPAY_KEY_ID and DJANGO_DEBUG == False:
    raise ValueError("Razorpay test keys are not allowed in production")


client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_SECRET_KEY))

def serialize_subscription_data(subscription_response):
    status = subscription_response.get("status")
    current_period_start = date_utils.timestamp_as_datetime(
        subscription_response.get("current_start")
    )
    current_period_end = date_utils.timestamp_as_datetime(
        subscription_response.get("current_end")
    )
    charge_at = date_utils.timestamp_as_datetime(
        subscription_response.get("charge_at")
    )
    cancel_at_period_end = subscription_response.get("cancel_at_cycle_end", False)
 
    return {
        "status": status,
        "current_period_start": current_period_start,
        "current_period_end": current_period_end,
        "charge_at": charge_at,
        "cancel_at_period_end": cancel_at_period_end,
    }

def create_customer(name="", email="", notes={}, raw=False):    
    response = client.customer.create(
                {
                    "name": name,
                    "email": email,
                    "notes": notes
                }
                )
    if raw:
        return response
    razorpay_id = response.get("id")
    return razorpay_id

def create_plan(
        name="",
        amount=99900, #in paise
        currency="INR",
        interval=1, # billing frequency count
        period="monthly", # daily, weekly, monthly, yearly
        notes={},
        raw=False):

    response = client.plan.create({
        "period": period,
        "interval": interval,
        "item": {
            "name": name,
            "amount": amount,   # in paise
            "currency": currency,
        },
        "notes": notes,
    })
    if raw:
        return response
    return response.get("id")  # "plan_XXXX"

def create_subscription(plan_id, customer_id=None, total_count=12, raw=False):
    data = {
        "plan_id": plan_id,
        "total_count": total_count,
        "customer_notify": 1
    }
    if customer_id:
        data["customer_id"] = customer_id
    response = client.subscription.create(data)
    if raw:
        return response
    return response

def get_subscription(razorpay_sub_id, raw=False):
    """
    Fetch a Razorpay subscription by its sub_XXXX ID.
    """
    response = client.subscription.fetch(razorpay_sub_id)
    if raw:
        return response
    return serialize_subscription_data(response)
 
 
def get_customer_active_subscriptions(customer_razorpay_id):
    """
    List all active subscriptions for a customer.
    """
    response = client.subscription.all({
        "customer_id": customer_razorpay_id,
    })
    # Filter active ones client-side since Razorpay doesn't support
    # status filtering on list endpoint the same way Stripe does
    items = response.get("items", [])
    return [s for s in items if s.get("status") == "active"]
 
 
def cancel_subscription(razorpay_sub_id, cancel_at_cycle_end=False, raw=False):
    """
    Cancel a Razorpay subscription.
    cancel_at_cycle_end=False → cancel immediately
    cancel_at_cycle_end=True  → cancel at end of current billing cycle(user retains access until period ends)
    """
    response = client.subscription.cancel(razorpay_sub_id, {
        "cancel_at_cycle_end": 1 if cancel_at_cycle_end else 0,
    })
    if raw:
        return response
    return serialize_subscription_data(response)
 
 
def get_subscription_for_checkout(razorpay_sub_id):
    """
    Called in your checkout success view after the user completes payment.
    NOTE: Razorpay does not have a session_id. Instead, after the frontend JS widget completes, you
    receive payment_id, subscription_id, and signature via POST.
    Verify the signature first, then call this function.
    """
    sub_response = get_subscription(razorpay_sub_id, raw=True)
    subscription_data = serialize_subscription_data(sub_response)
 
    return {
        "customer_id": sub_response.get("customer_id"),  # "cust_XXXX"
        "plan_id": sub_response.get("plan_id"),           # "plan_XXXX"
        "razorpay_sub_id": razorpay_sub_id,               # "sub_XXXX"
        **subscription_data,
    }

def verify_payment_signature(razorpay_payment_id, razorpay_subscription_id, razorpay_signature):
    """
    Verify the payment signature sent by Razorpay's frontend JS widget
    after a successful payment.
    """
    try:
        client.utility.verify_payment_signature({
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_subscription_id": razorpay_subscription_id,
            "razorpay_signature": razorpay_signature,
        })
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
 