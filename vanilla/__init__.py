__version__ = '0.1.2'

from django.views.generic import View
from vanilla.views import (
    GenericView, RedirectView, TemplateView, FormView
)
from vanilla.model_views import (
    GenericModelView, ListView, DetailView, CreateView, UpdateView, DeleteView
)
