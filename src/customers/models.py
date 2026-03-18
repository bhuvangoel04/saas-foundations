from django.db import models
from django.conf import settings 
import helpers.billing as billing
# Create your models here.

User = settings.AUTH_USER_MODEL

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # one stripe customer per user
    is_active = models.BooleanField(default=True)
    razorpay_id = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.razorpay_id:
            email = self.user.email
            name = self.user.username 
            if email != "" or email is not None:
                razorpay_id = billing.create_customer(name=name, email=email, raw=False)
                self.razorpay_id = razorpay_id
        super().save(*args, **kwargs)