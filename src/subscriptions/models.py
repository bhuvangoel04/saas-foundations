from django.db import models
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.conf import settings

User = settings.AUTH_USER_MODEL # outputs just the string "auth.User"


ALLOW_CUSTOM_GROUPS = True

SUBSCRIPTION_PERMISSIONS = [
            ("premium", "Premium Perms" ), # subscriptions.premium
            ("plus", "Plus Perm"), # subscriptions.plus
            ("free", "Free Perm") # subscriptions.free
        ]
# Create your models here.
class Subscription(models.Model):
    name = models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    # both groups and permissions so that each subscription can be associated to a group or groups and can be assigned permissions directly also
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(Permission, 
                                         limit_choices_to={
                                            "content_type__app_label":"subscriptions", 
                                            "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS]
                                            }
                                         )
    # Only show permissions belonging to the subscriptions app.
    
    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        # my custom permissions
        permissions = SUBSCRIPTION_PERMISSIONS
        
        
class UserSubscription(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE) # delete subs when user is deleted
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True) # its ok for a user to not have a subscription
    active = models.BooleanField(default=True)
    
    
    
def user_sub_post_save(sender, instance, *args, **kwargs):
    user_sub_instance = instance
    user = user_sub_instance.user
    subscription_obj = user_sub_instance.subscription
    groups_ids = []
    if subscription_obj is not None:
        groups = subscription_obj.groups.all()
        groups_ids = groups.values_list('id', flat=True) # create a list of groups ids
    groups = user_sub_instance.groups.all()
    user.groups.set(groups)
    if not ALLOW_CUSTOM_GROUPS:
        user.groups.set(groups) #sets new groups but removes from any other groups
    else:
        # create sets of current and subs groups so that you can apply union
        subs_qs = Subscription.objects.filter(active=True)
        if subscription_obj is not None:
            subs_qs = subs_qs.exclude(id=subscription_obj.id)
        subs_groups = subs_qs.values_list('group__id', flat=True)
        subs_groups_set = set(subs_groups)
        # groups_ids = groups.values_list('id', flat=True) 
        current_groups = user.groups.all().values_list('id', flat=True)
        group_ids_set = set(groups_ids)
        current_groups_set = set(current_groups) - subs_groups_set
        final_group_ids = list(group_ids_set | current_groups_set) # union
        user.groups.set(groups)
post_save.connect(user_sub_post_save, sender=UserSubscription)