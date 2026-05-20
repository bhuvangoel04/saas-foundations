from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from subscriptions.models import SubscriptionPrice, UserSubscription
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

    from customers.models import Customer
    customer, created = Customer.objects.get_or_create(user=request.user)

    if not customer.razorpay_id:
        email = request.user.email
        if not email:
            email = f"{request.user.username}@example.com"
        try:
            razorpay_id = billing.create_customer(
                name=request.user.username,
                email=email,
                notes={"user_id": request.user.id, "username": request.user.username},
                raw=False
            )
            customer.razorpay_id = razorpay_id
            customer.init_email = email
            customer.init_email_confirmed = True
            customer.save()
        except Exception as e:
            print("Error creating customer on checkout:", e)
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
    if request.method == "POST":
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_subscription_id = request.POST.get('razorpay_subscription_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # Verify signature
        is_valid = billing.verify_payment_signature(
            razorpay_payment_id=razorpay_payment_id,
            razorpay_subscription_id=razorpay_subscription_id,
            razorpay_signature=razorpay_signature
        )

        if is_valid:
            try:
                # Fetch subscription info
                sub_data = billing.get_subscription_for_checkout(razorpay_subscription_id)
                # Find corresponding subscription plan in db
                plan_id = sub_data.get("plan_id")
                price_obj = SubscriptionPrice.objects.filter(razorpay_plan_id=plan_id).first()
                subscription_obj = price_obj.subscription if price_obj else None

                # Update or create user subscription
                user_sub, created = UserSubscription.objects.get_or_create(user=request.user)
                user_sub.subscription = subscription_obj
                user_sub.razorpay_subscription_id = razorpay_subscription_id
                user_sub.status = sub_data.get('status')
                user_sub.current_period_start = sub_data.get('current_period_start')
                user_sub.current_period_end = sub_data.get('current_period_end')
                user_sub.charge_at = sub_data.get('charge_at')
                user_sub.cancel_at_period_end = sub_data.get('cancel_at_period_end')
                user_sub.save()
            except Exception as e:
                print("Error saving user subscription:", e)

    user_sub = getattr(request.user, 'usersubscription', None)
    context = {
        "user_sub": user_sub
    }
    return render(request, "billing/success.html", context)