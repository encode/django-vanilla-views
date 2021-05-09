from django.conf.urls import url

from example.notes.views import CreateNote, DeleteNote, EditNote, ListNotes

urlpatterns = [
    url(r"^$", ListNotes.as_view(), name="list_notes"),
    url(r"^create/$", CreateNote.as_view(), name="create_note"),
    url(r"^edit/(?P<pk>\d+)/$", EditNote.as_view(), name="edit_note"),
    url(r"^delete/(?P<pk>\d+)/$", DeleteNote.as_view(), name="delete_note"),
]
