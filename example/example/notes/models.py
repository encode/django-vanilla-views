# coding=utf-8
from django.db import models

class Note(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=100)
    complete = models.BooleanField(default=False)

    @property
    def checkbox_character(self):
        return '☑' if self.complete else '☐'

    class Meta:
        ordering = ('-created',)
