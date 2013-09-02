from django.conf.urls import patterns, include, url
from example.notes.models import Note

urlpatterns = patterns('example.notes.views',
    url(r'^$', 'list_notes', name='list_notes'),
    url(r'^create/$', 'create_note', name='create_note'),
    url(r'^edit/(?P<pk>\d+)/$', 'edit_note', name='edit_note'),
    url(r'^delete/(?P<pk>\d+)/$', 'delete_note', name='delete_note'),
)
