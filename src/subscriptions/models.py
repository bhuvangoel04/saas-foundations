from django.db import models
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.conf import settings

User = settings.AUTH_USER_MODEL # outputs just the string "auth.User"


ALLOW_CUSTOM_GROUPS = True

SUBSCRIPTION_PERMISSIONS = [
            ("premium", "Premium Perms" ), # subscriptions.premium
            ("plus", "Plus Perm"), # subscriptions.plus
            ("custom", "Custom Perm"),   # subscriptions.custom
        ]

#free tier - assign to all users on signup 
#plus tier - Starter subscribers
#premium tier - Premium subscribers
#custom tier - Enterprise subscribers

# Create your models here.
class Subscription(models.Model):
    name = models.CharField(max_length=120)
    subtitle = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    # both groups and permissions so that each subscription can be associated to a group or groups and can be assigned permissions directly also
    groups = models.ManyToManyField(Group, blank=True)
    permissions = models.ManyToManyField(Permission, 
                                         limit_choices_to={
                                            "content_type__app_label":"subscriptions", 
                                            "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS]
                                            }
                                         )
    # Only show permissions belonging to the subscriptions app.
    order = models.IntegerField(default=-1, help_text="Ordering on pricing page")
    featured = models.BooleanField(default=True, help_text="Featured on pricing page")
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    features = models.TextField(
        help_text="Features for pricing, separated by new line",
        blank=True,
        null=True
    )
 
    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        ordering = ["order", "featured", "-updated"]
        # my custom permissions
        permissions = SUBSCRIPTION_PERMISSIONS
    
    def get_features_as_list(self):
        if not self.features:
            return []
        return [x.strip() for x in self.features.split("\n")]
        
class SubscriptionPriceInterval(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    YEARLY = "yearly", "Yearly"

class SubscriptionPrice(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)

    razorpay_plan_id = models.CharField(

        max_length=120,

        null=True,

        blank=True,

        help_text="The plan_XXXX ID from Razorpay."

    )

    interval = models.CharField(

        max_length=120,

        default=SubscriptionPriceInterval.MONTHLY,

        choices=SubscriptionPriceInterval.choices

    )

    price = models.DecimalField(max_digits=10, decimal_places=2, default=999.00)

    order = models.IntegerField(default=-1, help_text="Ordering on pricing page")

    featured = models.BooleanField(default=True, help_text="Featured on pricing page")

    updated = models.DateTimeField(auto_now=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    @property

    def razorpay_interval(self):

        mapping = {

            SubscriptionPriceInterval.MONTHLY: "monthly",

            SubscriptionPriceInterval.YEARLY: "yearly",

        }

        return mapping.get(self.interval, "monthly")
    
        def save(self, *args, **kwargs):
            """
            Plans should be created manually in the Razorpay dashboard 
            and their plan ID pasted into razorpay_plan_id. This avoids accidental duplicate plan 
            creation on every admin save.
            """
            super().save(*args, **kwargs)
    
            # Ensure only one SubscriptionPrice per (subscription, interval) is featured
            if self.featured and self.subscription:
                SubscriptionPrice.objects.filter(
                    subscription=self.subscription,
                    interval=self.interval
                ).exclude(id=self.id).update(featured=False)

class SubscriptionStatus(models.TextChoices):
    """
    Razorpay subscription lifecycle statuses.
    https://razorpay.com/docs/payments/subscriptions/states/
    """
    CREATED = "created", "Created"  # Plan created, payment not yet collected
    AUTHENTICATED = "authenticated", "Authenticated" # Mandate registered, first charge pending
    ACTIVE = "active", "Active" # Subscription is live and charging
    PENDING = "pending", "Pending" # Charge attempt failed, retrying
    HALTED = "halted", "Halted" # Max retries exhausted, subscription paused
    CANCELLED = "cancelled", "Cancelled" # Cancelled by user or merchant
    COMPLETED = "completed", "Completed" # All billing cycles finished
    EXPIRED = "expired", "Expired" # Passed end date without activation

class UserSubscriptionQuerySet(models.QuerySet):
 
    def by_range(self, days_start=7, days_end=120):
        """Subscriptions whose current period ends within a date window."""
        now = timezone.now()
        range_start = (now + datetime.timedelta(days=days_start)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        range_end = (now + datetime.timedelta(days=days_end)).replace(
            hour=23, minute=59, second=59, microsecond=59
        )
        return self.filter(
            current_period_end__gte=range_start,
            current_period_end__lte=range_end
        )
 
    def by_days_left(self, days_left=7):
        """Subscriptions expiring exactly N days from now."""
        now = timezone.now()
        target = now + datetime.timedelta(days=days_left)
        day_start = target.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = target.replace(hour=23, minute=59, second=59, microsecond=59)
        return self.filter(
            current_period_end__gte=day_start,
            current_period_end__lte=day_end
        )
 
    def by_days_ago(self, days_ago=3):
        """Subscriptions that expired exactly N days ago."""
        now = timezone.now()
        target = now - datetime.timedelta(days=days_ago)
        day_start = target.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = target.replace(hour=23, minute=59, second=59, microsecond=59)
        return self.filter(
            current_period_end__gte=day_start,
            current_period_end__lte=day_end
        )
 
    def by_active_trialing(self):
        # users who should currently have access(both charged and free trial users)
        return self.filter(
            Q(status=SubscriptionStatus.ACTIVE) | # users with active subscriptions i.e. charged
            Q(status=SubscriptionStatus.AUTHENTICATED) # users authenticated but not yet charged
        )
 
    def by_user_ids(self, user_ids=None):
        qs = self
        if isinstance(user_ids, (list, int, str)):
            ids = user_ids if isinstance(user_ids, list) else [user_ids]
            qs = self.filter(user_id__in=ids)
        return qs

class UserSubscriptionManager(models.Manager):
    def get_queryset(self):
        return UserSubscriptionQuerySet(self.model, using=self._db)

class UserSubscription(models.Model):
    """
    Tracks a user's active Razorpay subscription.
    current_period_start / current_period_end: populated from Razorpay 
    webhook events (subscription.charged, subscription.activated).
    Razorpay sends these as Unix timestamps; convert to datetime before saving.
    charge_at: the next scheduled charge date, sent in webhook payloads 
    as `charge_at` (Unix timestamp). Useful for "next billing date" UI.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(
        Subscription, on_delete=models.SET_NULL, null=True, blank=True
    )
    razorpay_subscription_id = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        help_text="The sub_XXXX ID from Razorpay"
    )
    active = models.BooleanField(default=True)
    user_cancelled = models.BooleanField(default=False)
 
    # Populated from Razorpay webhooks: subscription.charged / subscription.activated
    original_period_start = models.DateTimeField(blank=True, null=True)
    current_period_start = models.DateTimeField(blank=True, null=True)
    current_period_end = models.DateTimeField(blank=True, null=True)
 
    # Razorpay-specific: next scheduled charge date (from webhook payload's `charge_at`)
    charge_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Next scheduled charge date from Razorpay (webhook: charge_at)"
    )
 
    cancel_at_period_end = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        null=True,
        blank=True
    )
 
    objects = UserSubscriptionManager()
 
    def __str__(self):
        return f"{self.user} — {self.subscription}"
 
    def get_absolute_url(self):
        return reverse("user_subscription")
 
    def get_cancel_url(self):
        return reverse("user_subscription_cancel")
 
    @property
    def is_active_status(self):
        """
        Consider a subscription 'active' if Razorpay reports it as 
        active or authenticated (mandate registered, first charge pending).
        """
        return self.status in [
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.AUTHENTICATED,
        ]
 
    @property
    def plan_name(self):
        if not self.subscription:
            return None
        return self.subscription.name
 
    def serialize(self):
        return {
            "plan_name": self.plan_name,
            "status": self.status,
            "current_period_start": self.current_period_start,
            "current_period_end": self.current_period_end,
            "charge_at": self.charge_at,
        }
 
    @property
    def billing_cycle_anchor(self):
        """
        When upgrading/renewing, pass this Unix timestamp to Razorpay's 
        start_at parameter so the new subscription begins at the current 
        period's end (avoids double-charging the user).
        """
        if not self.current_period_end:
            return None
        return int(self.current_period_end.timestamp())
 
    def save(self, *args, **kwargs):
        if (self.original_period_start is None and
                self.current_period_start is not None):
            self.original_period_start = self.current_period_start
        super().save(*args, **kwargs)

def user_sub_post_save(sender, instance, *args, **kwargs):
    user_sub_instance = instance
    user = user_sub_instance.user
    subscription_obj = user_sub_instance.subscription 
    # Collect group IDs granted by the current subscription
    groups_ids = []
    if subscription_obj is not None:
        groups_ids = subscription_obj.groups.values_list("id", flat=True)
 
    if not ALLOW_CUSTOM_GROUPS:
        # Strict: user gets exactly and only their subscription's groups
        user.groups.set(groups_ids)
    else:
        # Permissive: preserve any groups the user has that don't belong to 
        # other active subscriptions (custom/manually-assigned groups are kept;
        # only subscription-managed groups are swapped out).
        other_subs_qs = Subscription.objects.filter(active=True)
        if subscription_obj is not None:
            other_subs_qs = other_subs_qs.exclude(id=subscription_obj.id)
 
        # All groups owned by other active subscriptions — strip these
        other_subs_groups_set = set(
            other_subs_qs.values_list("groups__id", flat=True)
        )
 
        current_groups_set = set(user.groups.values_list("id", flat=True))
        # Drop other-subscription groups, keep everything else
        preserved_groups = current_groups_set - other_subs_groups_set
 
        final_group_ids = list(set(groups_ids) | preserved_groups)
        user.groups.set(final_group_ids)
 
 
post_save.connect(user_sub_post_save, sender=UserSubscription)