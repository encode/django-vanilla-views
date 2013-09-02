from django.conf.urls import patterns, include, url
from vanilla import CreateView, ListView
from example.notes.models import Note

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=Note), name='note_list'),
    url(r'^create$', CreateView.as_view(model=Note), name='note_create'),
)
