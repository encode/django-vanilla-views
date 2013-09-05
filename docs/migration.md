#### `pk_url_field`, `slug_url_field`, `slug_url_kwarg`, `get_slug_field()`

**These have been replaced** with a simpler style using `lookup_field` and `lookup_url_kwarg`.

If you need non-pk based lookup, specify `lookup_field` on the view:

    class AccountListView(ListView):
        model = Account
        lookup_field = 'slug'

If you need a differing URL kwarg from the model field name, you should also set `lookup_url_kwarg`.

    class AccountListView(ListView):
        model = Account
        lookup_field = 'slug'
        lookup_url_kwarg = 'account_name'

For more complex lookups, override `get_object()`, like so:

    class AccountListView(ListView):
		def get_object(self):
		    queryset = self.get_queryset()
		    return get_object_or_404(queryset, slug=self.kwargs['slug'], owner=self.request.user)

#### `initial`, `get_initial()`, `get_form_kwargs()`

**These are all removed**.  If you need to override how the form is intialized, just override `get_form()`.

For example, instead of this:

	def get_form_kwargs(self):
	    kwargs = super(AccountEditView, self).get_form_kwargs
	    kwargs['user'] = self.request.user
	    return kwargs

You should write this:

    def get_form(self, data, files, instance=None):
        return AccountForm(data, files, user=self.request.user, instance=instance)

Or this:

    def get_form(self, data, files, instance=None):
        cls = self.get_form_class()
        return cls(data, files, user=self.request.user, instance=instance)

#### `template_name_field`

**This is removed**.  If you need to dynamically determine template names, you should override `get_template_names()`.

    def get_template_names(self):
        return [self.object.template]

#### `content_type`, `response_cls`

**These are removed**.  If you need to customize how responses are rendered, you should override `render_to_response()`.

    def render_to_response(context):
        return JSONResponse(request, context)

If you needed to override the content type, you might write:

    def render_to_response(context):
    	template = self.get_template_names()
        return TemplateResponse(request, template, context, content_type='text/plain')

#### `paginator_cls`, `paginate_orphans`, `get_paginate_orphans()`

**These are removed**.  If you need to customize how the paginator is instantiated, you should override `get_paginator()`.

    def get_paginator(self, queryset, page_size):
        return CustomPaginator(queryset, page_size, orphans=3)

#### `get_success_url()`

**This is removed**, as it introduces an uneccessary layer of indirection.  It's cleaner to override `form_valid()` instead.  So, instead of this:

    def get_success_url():
        return self.object.account_activated_url()

Write this:

    def form_valid(form):
        self.object = form.save()
        return HttpResponseRedirect(self.object.account_activated_url())

It's hardly any more code, and there's no indirection or implicit behavior going on here.
You'll thank yourself when you later need to add some more behavior to `form_valid()`.  Instead of ending up with code like this:

    def get_success_url():
        return self.object.account_activated_url()

    def form_valid(form):
        send_activation_email(self.request.user)
        return super(AccountActivationView, self).form_valid(form)

You'll instead have a simpler, more direct style:

    def form_valid(form):
        send_activation_email(self.request.user)
        self.object = form.save()
        return HttpResponseRedirect(self.object.account_activated_url())

#### `paginate_queryset()`

The call signature and return value for this method **have been simplified**.  Instead of this:

    paginate_by = self.get_paginate_by()
	(page, paginator, queryset, is_paginated) = self.paginate_queryset(queryset, paginate_by)

You should just write this:

    page = self.paginate_queryset(queryset)

Which will either return a page object, or `None` if pagination is not configured on the view.
The page object contains a `.paginator` attribute and a `.object_list` attribute, so you still have access to the same set of information.

#### `get_object()`

The call signature **has been simplified**.  The `get_object()` method no longer takes an optional `queryset` parameter.

#### `get_form_class()`

The behavior has been made **slightly less magical**.  In the regular Django implementation, if neither `model` or `form_class` is specified on the view, then `get_form_class()` will fallback to attempting to automatically generate a form class based on either the object currently being operated on, or failing that to generate a form class by calling `get_queryset` and determining a default model form class from that.

In `django-vanilla-views`, if neither the `model` or `form_class` is specified, it's a configuration error.  If you need any more advanced behavior that that, you should override `get_form_class()`.

#### `get_template_name()`

The behavior has been made **slightly less magical**...

