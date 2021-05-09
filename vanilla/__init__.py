__version__ = '2.0.0'
__all__ = (
    'View', 'GenericView', 'GenericModelView',
    'RedirectView', 'TemplateView', 'FormView',
    'ListView', 'DetailView', 'CreateView', 'UpdateView', 'DeleteView'
)

from django.views.generic import RedirectView, View
from vanilla.views import (
    GenericView, TemplateView, FormView
)
from vanilla.model_views import (
    GenericModelView, ListView, DetailView, CreateView, UpdateView, DeleteView
)
