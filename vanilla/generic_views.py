from django.core.exceptions import ImproperlyConfigured
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.generic import View


class GenericView(View):
    initial = {}
    form_class = None
    template_name = None

    def get_form_class(self):
        """
        Returns the form class to use in this view.
        """
        if self.form_class is not None:
            return self.form_class

        raise ImproperlyConfigured("'%s' must either define 'form_class' or "
            "override 'get_form_class()'" % self.__class__.__name__)

    def get_template_names(self):
        if self.template_name is not None:
            return [self.template_name]

        raise ImproperlyConfigured("'%s' must either define 'template_name' "
            "or override 'get_template_names()'" % self.__class__.__name__)

    def get_form(self, data=None, files=None):
        cls = self.get_form_class()
        return cls(data=data, files=files, initial=self.initial.copy())

    def get_context(self, **kwargs):
        kwargs['view'] = self
        return kwargs

    def get_response(self, context):
        return TemplateResponse(
            request=self.request,
            template=self.get_template_names(),
            context=context
        )

class RedirectView(View):
    url = None

    def get(self, request, *args, **kwargs):
        if not self.url:
            msg = "'%s' must define 'url'" % self.__class__.__name__
            raise ImproperlyConfigured(msg)
        return HttpResponseRedirect(self.url % self.kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class TemplateView(GenericView):
    def get(self, request, *args, **kwargs):
        context = self.get_context()
        return self.get_response(context)


class FormView(GenericView):
    success_url = None

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context(form=form)
        return self.get_response(context)


    def post(self, request):
        form = self.get_form(data=request.POST, files=request.FILES)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        if self.success_url is None:
            msg = "'%s' must define 'url'" % self.__class__.__name__
            raise ImproperlyConfigured(msg)
        return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        return TemplateResponse(
            request=request,
            template=self.get_template_names(),
            context=self.get_context(form=form)
        )
