from django.core.urlresolvers import reverse_lazy
from example.notes.models import Note
from vanilla import CreateView, DeleteView, ListView, UpdateView

class ListNotes(ListView):
    model = Note


class CreateNote(CreateView):
    model = Note
    success_url = reverse_lazy('list_notes')


class EditNote(UpdateView):
    model = Note
    success_url = reverse_lazy('list_notes')


class DeleteNote(DeleteView):
    model = Note
    success_url = reverse_lazy('list_notes')


list_notes = ListNotes.as_view()
create_note = CreateNote.as_view()
edit_note = EditNote.as_view()
delete_note = DeleteNote.as_view()
