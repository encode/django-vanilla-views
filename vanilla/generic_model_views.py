from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator
from django.forms import models as model_forms
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.generic import View


class GenericModelView(View):
    """
    Base class for all model generic views.
    """
    model = None

    queryset = None
    form_class = None
    template_name = None
    context_object_name = None

    lookup_field = 'pk'
    initial = {}
    template_name_suffix = None

    paginate_by = None
    paginator_class = Paginator

    def get_object(self):
        """
        Returns the object the view is displaying.
        """
        queryset = self.get_queryset()
        lookup_value = self.kwargs.get(self.lookup_field)
        if lookup_value is None:
            raise ImproperlyConfigured("Lookup field '%s' was not provided"
            " in view kwargs to '%s'" %
            (self.lookup_field, self.__class__.__name__))
        lookup_kwargs = {self.lookup_field: lookup_value}
        return get_object_or_404(queryset, **lookup_kwargs)

    def get_queryset(self):
        """
        Returns the base queryset for the view.

        Either used as a list of objects to display, or as the queryset
        from which to perform the individual object lookup.
        """
        if self.queryset is not None:
            return self.queryset._clone()

        if self.model is not None:
            return self.model._default_manager.all()

        raise ImproperlyConfigured("'%s' must either define 'queryset' or "
            "'model', or override 'get_queryset()'" % self.__class__.__name__)

    def get_form_class(self):
        """
        Returns the form class to use in this view.
        """
        if self.form_class is not None:
            return self.form_class

        if self.model is not None:
            return model_forms.modelform_factory(self.model)

        raise ImproperlyConfigured("'%s' must either define 'form_class' or "
            "'model' and 'template_name_suffix', or override "
            "'get_form_class()'" % self.__class__.__name__)

    def get_template_names(self):
        """
        Returns a list of template names to use when rendering the response.
        """
        if self.template_name is not None:
            return [self.template_name]

        if self.model is not None and self.template_name_suffix is not None:
            return ["%s/%s%s.html" % (
                self.model._meta.app_label,
                self.model._meta.object_name.lower(),
                self.template_name_suffix
            )]

        raise ImproperlyConfigured("'%s' must either define 'template_name' "
            "or 'model', or override 'get_template_names()'" %
            self.__class__.__name__)

    def get_form(self, data=None, files=None, instance=None):
        """
        Return a form instance.
        """
        cls = self.get_form_class()
        return cls(
            data=data,
            files=files,
            instance=instance,
            initial=self.initial.copy()
        )

    def get_paginate_by(self):
        """
        Return the size of pages to use with pagination.
        """
        return self.paginate_by

    def paginate_queryset(self, queryset):
        """
        Paginate a queryset if required, either returns a page object,
        or returns `None` if pagination is not configured for this view.
        """
        page_size = self.get_paginate_by()
        if not page_size:
            return None

        paginator = self.paginator_class(queryset, page_size)
        page_kwarg = self.kwargs.get(self.page_kwarg)
        page_query_param = self.request.GET.get(self.page_kwarg)
        page = page_kwarg or page_query_param or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                msg = "Page is not 'last', nor can it be converted to an int."
                raise Http404(_(msg))

        try:
            return paginator.page(page_number)
        except InvalidPage as exc:
            msg = 'Invalid page (%(page_number)s): %(message)s' % {
                'page_number': page_number,
                'message': str(exc)
            }
            raise Http404(_(msg))

    def get_context(self, **kwargs):
        """
        Returns a dictionary to use as the context of the response.

        Takes a set of keyword arguments to use as the base context,
        and additionally includes:

        * `view`
        * `object` if the view includes an `object` attribute.
        * `object_list` if the view includes an `object_list` attribute.

        TODO...
        """
        kwargs['view'] = self

        obj = getattr(self, 'object', None)
        obj_list = getattr(self, 'object_list', None)

        if self.context_object_name is not None:
            context_object_name = self.context_object_name
        elif self.model is not None:
            context_object_name = self.model._meta.object_name.lower()
        else:
            context_object_name = None

        if obj:
            kwargs['object'] = obj
            if context_object_name:
                kwargs[context_object_name] = obj

        if obj_list:
            kwargs['object_list'] = obj_list
            if context_object_name:
                kwargs[context_object_name + '_list'] = obj_list

        return kwargs

    def get_response(self, context):
        return TemplateResponse(
            request=self.request,
            template=self.get_template_names(),
            context=context
        )



#### Model Views

class ListView(GenericModelView):
    template_name_suffix = '_list'

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        page = self.paginate_queryset(self.object_list)
        context = self.get_context(
            page=page,
            is_paginated=page is not None,
            paginator=page.paginator if (page is not None) else None,
        )
        return self.get_response(context)


class DetailView(GenericModelView):
    template_name_suffix = '_detail'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context()
        return self.get_response(context)



class CreateView(GenericModelView):
    success_url = None
    template_name_suffix = '_form'

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
        form.save()
        try:
            url = self.success_url or self.object.get_absolute_url()
        except AttributeError:
            msg = ("No URL to redirect to.  '%s' must provide 'success_url' "
                "or define a 'get_absolute_url' method on the Model." %
                self.__class__.__name__)
            raise ImproperlyConfigured(msg)
        return HttpResponseRedirect(url)

    def form_invalid(self, form):
        context = self.get_context(form=form)
        return self.get_response(context)



class UpdateView(GenericModelView):
    success_url = None
    template_name_suffix = '_form'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(instance=self.object)
        context = self.get_context(form=form)
        return self.get_response(context)


    def post(self, request):
        self.object = self.get_object()
        form = self.get_form(
            data=request.POST,
            files=request.FILES,
            instance=self.object
        )

        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        try:
            url = self.success_url or self.object.get_absolute_url()
        except AttributeError:
            msg = ("No URL to redirect to.  '%s' must provide 'success_url' "
                "or define a 'get_absolute_url' method on the Model." %
                self.__class__.__name__)
            raise ImproperlyConfigured(msg)
        return HttpResponseRedirect(url)

    def form_invalid(self, form):
        context = self.get_context(form=form)
        return self.get_response(context)


class DeleteView(GenericModelView):
    success_url = None
    template_name_suffix = '_detail'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context()
        return self.get_response(context)


    def post(self):
        self.object = self.get_object()
        self.object.delete()
        if self.success_url is None:
            msg = ("No URL to redirect to.  '%s' must define 'success_url'" %
                self.__class__.__name__)
            raise ImproperlyConfigured(msg)
        return HttpResponseRedirect(self.success_url)
