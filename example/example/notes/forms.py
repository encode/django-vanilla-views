# coding=utf-8
from django.forms import ModelForm
from .models import Note


class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ['message', 'complete']
