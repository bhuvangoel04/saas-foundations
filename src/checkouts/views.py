from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
# Create your views here.

def product_price_redirect_view(request, price_id=None, *args, **kwargs):
    request.session['checkout_price_id'] = price_id
    return redirect("/checkout")

@login_required
def checkout_redirect_view(request):
    checkout_price_id = request.session.get('checkout_price_id')
    try:
        obj = SubscriptionPrice.objects.get(id=checkout_price_id)  
    except:
        obj = None    
    if obj is None or checkout_price_id is None:
        return redirect('pricing')
    customer_razorpay_id = request.user.customer.razorpay_id
    redirect("/checkout/abc")

@login_required
def checkout_success_view(request):
    pass
