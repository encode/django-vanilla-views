#coding: utf-8
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.generic import View


class GenericView(View):
    """
    Base class for the template and form views.
    """
    form_class = None
    template_name = None

    def get_form_class(self):
        """
        Returns the form class to use in this view.
        """
        if self.form_class is not None:
            return self.form_class

        msg = "'%s' must either define 'form_class' or override 'get_form_class()'"
        raise ImproperlyConfigured(msg % self.__class__.__name__)

    def get_template_names(self):
        """
        Returns a set of template names that may be used when rendering
        the response.
        """
        if self.template_name is not None:
            return [self.template_name]

        msg = "'%s' must either define 'template_name' or override 'get_template_names()'"
        raise ImproperlyConfigured(msg % self.__class__.__name__)

    def get_form(self, data=None, files=None):
        """
        Given `data` and `files` QueryDicts, returns a form.
        """
        cls = self.get_form_class()
        return cls(data=data, files=files)

    def get_context(self, **kwargs):
        """
        Takes a set of keyword arguments to use as the base context, and
        returns a context dictionary to use for the view, additionally adding
        in 'view'.
        """
        kwargs['view'] = self
        return kwargs

    def render_to_response(self, context):
        """
        Given a context dictionary, returns an HTTP response.
        """
        return TemplateResponse(
            request=self.request,
            template=self.get_template_names(),
            context=context
        )

class RedirectView(View):
    url = None
    pattern_name = None
    permanent = True

    def get(self, request, *args, **kwargs):
        if self.url:
            url = self.url % kwargs
        elif self.pattern_name:
            url = reverse(self.pattern_name, args=args, kwargs=kwargs)
        else:
            msg = "'%s' must define 'url' or 'pattern_name'"
            raise ImproperlyConfigured(msg % self.__class__.__name__)

        if self.permanent:
            return HttpResponsePermanentRedirect(url)
        return HttpResponseRedirect(url)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class TemplateView(GenericView):
    def get(self, request, *args, **kwargs):
        context = self.get_context()
        return self.render_to_response(context)


class FormView(GenericView):
    success_url = None

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context(form=form)
        return self.render_to_response(context)

    def post(self, request):
        form = self.get_form(data=request.POST, files=request.FILES)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        if self.success_url is None:
            msg = "'%s' must define 'success_url' or override `form_valid()`"
            raise ImproperlyConfigured(msg % self.__class__.__name__)
        return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        context = self.get_context(form=form)
        return self.render_to_response(context)
