from django.db import models
from django.conf import settings 
from django.contrib.auth.models import Group
import helpers.billing as billing
from django.contrib.auth import get_user_model
from allauth.account.signals import (
    user_signed_up as allauth_user_signedup,
    email_confirmed as allauth_email_confirmed
)

# Create your models here.

User = settings.AUTH_USER_MODEL

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # one stripe customer per user
    is_active = models.BooleanField(default=True)
    razorpay_id = models.CharField(max_length=255, null=True, blank=True)
    init_email = models.EmailField(blank=True, null=True) # initial email available
    init_email_confirmed = models.BooleanField(default=False) # initial email verified/confirmed

    def __str__(self):
        return f"{self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.razorpay_id:
            # create razorpay customer only when email is confirmed
            if self.init_email and self.init_email_confirmed:
                email = self.init_email
                name = self.user.username 
                if email != "" and email is not None:
                    razorpay_id = billing.create_customer(name=name, email=email,notes={"user_id":self.user.id, "username":self.user.username}, raw=False)
                    self.razorpay_id = razorpay_id
        super().save(*args, **kwargs)

# signal receivers
# when user signs up
def allauth_user_signedup_handler(request, user, *args, **kwargs):
    email = user.email
    Customer.objects.create(
        user=user, 
        init_email=email, 
        init_email_confirmed=False
    )
    
allauth_user_signedup.connect(allauth_user_signedup_handler, sender=get_user_model())

# when email is confirmed
def allauth_email_confirmed_handler(request, email_address, *args, **kwargs):
    qs =Customer.objects.filter( 
        # email_address is an allauth EmailAddress instance, not a plain string
        init_email=email_address.email, # .email extracts the string here 
        init_email_confirmed=False,
    )
    for obj in qs:
        obj.init_email_confirmed = True
        obj.save()
        # add user to free tier once the email is confirmed
        user = obj.user
        free_tier = Group.objects.get(name="free tier")

        if not user.groups.filter(name="free tier").exists():
            user.groups.add(free_tier)

allauth_email_confirmed.connect(allauth_email_confirmed_handler, sender=get_user_model())
