from django.db import models

# Create your models here.

class Analysis(models.Model):
    facts = models.TextField()
    issues = models.TextField()
    rules = models.TextField()
    analysis = models.TextField()
    conclusion = models.TextField()

    class Meta:
        app_label = 'firac'