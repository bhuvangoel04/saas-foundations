# syntax to create Django commands to be run with python manage.py command
from django.core.management.base import BaseCommand
from typing import Any
# basecommand provided by django to create commands

from subscriptions.models import Subscription
# class below should always be named "Command"
class Command(BaseCommand):
    
    def handle(self, *args: Any, **options: Any):
        print("Hello world!")
        qs = Subscription.objects.filter(active=True)
        for obj in qs:
            # print(obj.groups.all())
            # syncing the permissions to groups added in the subscription objects in admin panel
            sub_perms = obj.permissions.all()
            for group in obj.groups.all():
                for per in obj.permissions.all():
                    # group.permissions.add(per)
                    group.permissions.set(sub_perms) # set is better instead of add to avoid repeated addition
            # print(obj.permissions.all())
        