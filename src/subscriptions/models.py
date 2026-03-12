from django.db import models
from django.contrib.auth.models import Group, Permission


SUBSCRIPTION_PERMISSIONS = [
            ("premium", "Premium Perms" ), # subscriptions.premium
            ("plus", "Plus Perm"), # subscriptions.plus
            ("free", "Free Perm") # subscriptions.free
        ]
# Create your models here.
class Subscription(models.Model):
    name = models.CharField(max_length=120)
    # both groups and permissions so that each subscription can be associated to a group or groups and can be assigned permissions directly also
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(Permission, 
                                         limit_choices_to={
                                            "content_type__app_label":"subscriptions", 
                                            "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS]
                                            }
                                         )
    # Only show permissions belonging to the subscriptions app.
    
    class Meta:
        # my custom permissions
        permissions = SUBSCRIPTION_PERMISSIONS