from django.db import models

class Note(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=100)
    complete = models.BooleanField(default=False)
