from example.notes.models import Note
from example.notes.forms import NoteForm
from vanilla import CreateView, DeleteView, ListView, UpdateView

try:
    from django.urls import reverse_lazy  # django 1.11+
except ImportError:
    from django.core.urlresolvers import reverse_lazy


class ListNotes(ListView):
    model = Note


class CreateNote(CreateView):
    model = Note
    form_class = NoteForm
    success_url = reverse_lazy('list_notes')


class EditNote(UpdateView):
    model = Note
    form_class = NoteForm
    success_url = reverse_lazy('list_notes')


class DeleteNote(DeleteView):
    model = Note
    success_url = reverse_lazy('list_notes')
