from django.contrib import admin
from .models import Subscription, SubscriptionPrice, UserSubscription

class SubscriptionPriceInline(admin.TabularInline):
    # tabular inline allows us to add related objects in the same page as the parent object
    model = SubscriptionPrice
    extra = 0             # how many empty rows to show for adding new prices
    fields = ["interval", "price", "featured"]
    readonly_fields = ["razorpay_plan_id"] 
    # extra = 1 means one blank row is shown ready to fill in

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["name", "active", "featured", "order"]
    filter_horizontal = ["groups", "permissions"]
    inlines = [SubscriptionPriceInline]   # attach the inline here
    # no need to add subscription then save then add price in subscription price


@admin.register(SubscriptionPrice)
class SubscriptionPriceAdmin(admin.ModelAdmin):
    list_display = ["subscription", "razorpay_plan_id", "interval", "price", "featured"]


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "subscription", "status", "active", "current_period_end"]
    search_fields = ["user__username", "user__email", "razorpay_subscription_id"]
