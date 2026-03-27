from django.shortcuts import render
from subscriptions.models import SubscriptionPrice, SubscriptionPriceInterval
# Create your views here.
def subscription_price_view(request):
    qs = SubscriptionPrice.objects.filter(featured=True)
    monthly_qs = qs.filter(interval=SubscriptionPriceInterval.MONTHLY)
    yearly_qs = qs.filter(interval=SubscriptionPriceInterval.YEARLY)
    context = {
        "monthly_qs": monthly_qs,
        "yearly_qs": yearly_qs,
    }
    return render(request, "subscriptions/pricing.html", context)