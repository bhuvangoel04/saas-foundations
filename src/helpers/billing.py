from django.template.defaultfilters import default
import razorpay
from decouple import config

DJANGO_DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)
RAZORPAY_SECRET_KEY = config("RAZORPAY_SECRET_KEY", default="", cast=str)
RAZORPAY_KEY_ID = config("RAZORPAY_KEY_ID")

if "rzp_test" in RAZORPAY_KEY_ID and DJANGO_DEBUG == False:
    raise ValueError("Razorpay test keys are not allowed in production")


client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_SECRET_KEY))

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