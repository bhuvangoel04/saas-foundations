from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from subscriptions.models import SubscriptionPrice
import helpers.billing as billing


def product_price_redirect_view(request, price_id=None, *args, **kwargs):
    request.session['checkout_price_id'] = price_id
    return redirect("/checkout/")


@login_required
def checkout_redirect_view(request):
    checkout_price_id = request.session.get('checkout_price_id')

    if not checkout_price_id:
        return redirect('pricing')

    try:
        obj = SubscriptionPrice.objects.get(id=checkout_price_id)
    except SubscriptionPrice.DoesNotExist:
        return redirect('pricing')

    customer = request.user.customer

    if not customer.razorpay_id:
        return redirect('pricing')

    # Create Razorpay Subscription
    try:
        subscription = billing.create_subscription(
            plan_id=obj.razorpay_plan_id,
            customer_id=customer.razorpay_id
        )
    except Exception as e:
        print("Error creating subscription:", e)
        return redirect('pricing')

    context = {
        "subscription_id": subscription.get("id"),
        "razorpay_key": billing.RAZORPAY_KEY_ID,
        "plan": obj.subscription.name,
        "price": obj.price
    }

    return render(request, "billing/checkout.html", context)


@login_required
def checkout_success_view(request):
    return render(request, "billing/success.html", {})