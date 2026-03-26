from django.contrib import admin
from .models import Subscription, SubscriptionPrice, UserSubscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["name", "active", "featured", "order"]
    filter_horizontal = ["groups", "permissions"]


@admin.register(SubscriptionPrice)
class SubscriptionPriceAdmin(admin.ModelAdmin):
    list_display = ["subscription", "razorpay_plan_id", "interval", "price", "featured"]


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "subscription", "status", "active", "current_period_end"]
    search_fields = ["user__username", "user__email", "razorpay_subscription_id"]