# syntax to create Django commands to be run with python manage.py command
from django.core.management.base import BaseCommand
from typing import Any
# basecommand provided by django to create commands
# class below should always be named "Command"
class Command(BaseCommand):
    
    def handle(self, *args: Any, **options: Any):
        print("Hello world!")