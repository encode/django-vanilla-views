from django.views.generic import RedirectView, View

from vanilla.model_views import (
    CreateView,
    DeleteView,
    DetailView,
    GenericModelView,
    ListView,
    UpdateView,
)
from vanilla.views import FormView, GenericView, TemplateView

__version__ = "3.0.0"
__all__ = (
    "View",
    "GenericView",
    "GenericModelView",
    "RedirectView",
    "TemplateView",
    "FormView",
    "ListView",
    "DetailView",
    "CreateView",
    "UpdateView",
    "DeleteView",
)
