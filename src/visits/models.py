from django.db import models

# Create your models here.
class PageVisit(models.Model):
    # id ->hidden ->autofield Auto incremented
    path = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    