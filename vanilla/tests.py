from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Page, Paginator
from django.db import models
from django.forms import fields, BaseForm, Form, ModelForm
from django.http import Http404
from django.test import RequestFactory, TestCase
from vanilla import *
import types
import warnings


class Example(models.Model):
    text = models.CharField(max_length=10)

    class Meta:
        ordering = ('id',)


class ExampleForm(Form):
    text = fields.CharField(max_length=10)


class InstanceOf(object):
    """
    We use this sentinal object together with our 'assertContext' helper method.

    Used to ensure that a particular context value is an object of the given
    type, without requiring a specific fixed value.  Useful for form context,
    and other complex instances.
    """
    def __init__(self, expected_type):
        self.expected_type = expected_type


def create_instance(text=None, quantity=1):
    for idx in range(quantity):
        text = text or ('example %d' % idx)
        Example.objects.create(text=text)


class BaseTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        super(BaseTestCase, self).setUp()

    def assertFormError(self, response, form, field, errors, msg_prefix=''):
        # Hack to get around the fact that we're using request factory,
        # instead of the full test client.
        response.context = response.context_data
        return super(BaseTestCase, self).assertFormError(response, form, field, errors, msg_prefix)

    def assertContext(self, response, expected):
        # Ensure the keys all match.
        # Note that this style ensures we get nice descriptive failures.
        for key in expected.keys():
            self.assertTrue(key in response.context_data,
                "context missing key '%s'" % key)
        for key in response.context_data.keys():
            self.assertTrue(key in expected,
                "context contains unexpected key '%s'" % key)

        # Ensure all the values match.
        for key, val in response.context_data.items():
            expected_val = expected[key]
            if isinstance(val, (models.query.QuerySet)):
                val = list(val)
            if isinstance(expected_val, models.query.QuerySet):
                expected_val = list(expected_val)

            if isinstance(expected_val, InstanceOf):
                self.assertTrue(isinstance(val, expected_val.expected_type),
                    "context['%s'] contained type '%s', but expected type '%s'"
                    % (key, type(val), expected_val.expected_type))
            else:
                self.assertEqual(val, expected_val,
                    "context['%s'] contained '%s', but expected '%s'" %
                    (key, val, expected_val))

    def get(self, view, *args, **kwargs):
        request = self.factory.get('/')
        return view(request, *args, **kwargs)

    def post(self, view, *args, **kwargs):
        data = kwargs.pop('data', {})
        request = self.factory.post('/', data=data)
        return view(request, *args, **kwargs)


class TestDetail(BaseTestCase):
    def test_detail(self):
        create_instance(quantity=3)
        pk = Example.objects.all()[0].pk
        view = DetailView.as_view(model=Example)
        response = self.get(view, pk=pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['vanilla/example_detail.html'])
        self.assertContext(response, {
            'object': Example.objects.get(pk=pk),
            'example': Example.objects.get(pk=pk),
            'view': InstanceOf(View)
        })

    def test_detail_not_found(self):
        create_instance(quantity=3)
        view = DetailView.as_view(model=Example)
        self.assertRaises(Http404, self.get, view, pk=999)

    def test_detail_misconfigured_urlconf(self):
        # If we don't provide 'pk' in the URL conf,
        # we should expect an ImproperlyConfigured exception.
        create_instance(quantity=3)
        view = DetailView.as_view(model=Example)
        self.assertRaises(ImproperlyConfigured, self.get, view, slug=999)

    def test_detail_misconfigured_template_name(self):
        # If don't provide 'model' or 'template_name',
        # we should expect an ImproperlyConfigured exception.
        create_instance(quantity=3)
        pk = Example.objects.all()[0].pk
        view = DetailView.as_view(queryset=Example.objects.all())
        self.assertRaises(ImproperlyConfigured, self.get, view, pk=pk)

    def test_detail_misconfigured_queryset(self):
        # If don't provide 'model' or 'queryset',
        # we should expect an ImproperlyConfigured exception.
        create_instance(quantity=3)
        pk = Example.objects.all()[0].pk
        view = DetailView.as_view(template_name='example.html')
        self.assertRaises(ImproperlyConfigured, self.get, view, pk=pk)

    def test_detail_missing_context_object_name(self):
        # If don't provide 'model' or 'context_object_name',
        # then the context will only contain the 'object' key.
        create_instance(quantity=3)
        pk = Example.objects.all()[0].pk
        view = DetailView.as_view(queryset=Example.objects.all(), template_name='example.html')
        response = self.get(view, pk=pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['example.html'])
        self.assertContext(response, {
            'object': Example.objects.get(pk=pk),
            'view': InstanceOf(View)
        })


class TestList(BaseTestCase):
    def test_list(self):
        create_instance(quantity=3)
        view = ListView.as_view(model=Example)
        response = self.get(view)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['vanilla/example_list.html'])
        self.assertContext(response, {
            'object_list': Example.objects.all(),
            'example_list': Example.objects.all(),
            'view': InstanceOf(View),
            'page_obj': None,
            'paginator': None,
            'is_paginated': False
        })

    def test_empty_list(self):
        view = ListView.as_view(model=Example)
        response = self.get(view)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['vanilla/example_list.html'])
        self.assertContext(response, {
            'object_list': [],
            'example_list': [],
            'view': InstanceOf(View),
            'page_obj': None,
            'paginator': None,
            'is_paginated': False
        })

    def test_empty_list_not_found(self):
        view = ListView.as_view(model=Example, allow_empty=False)
        self.assertRaises(Http404, self.get, view, pk=999)

    def test_paginated_list(self):
        create_instance(quantity=30)
        view = ListView.as_view(model=Example, paginate_by=10)
        response = self.get(view)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['vanilla/example_list.html'])
        self.assertContext(response, {
            'object_list': Example.objects.all()[:10],
            'example_list': Example.objects.all()[:10],
            'view': InstanceOf(View),
            'page_obj': InstanceOf(Page),
            'paginator': InstanceOf(Paginator),
            'is_paginated': True
        })

    def test_paginated_list_valid_page_specified(self):
        create_instance(quantity=30)
        view = ListView.as_view(model=Example, paginate_by=10)
        response = self.get(view, page=2)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['vanilla/example_list.html'])
        self.assertContext(response, {
            'object_list': Example.objects.all()[10:20],
            'example_list': Example.objects.all()[10:20],
            'view': InstanceOf(View),
            'page_obj': InstanceOf(Page),
            'paginator': InstanceOf(Paginator),
            'is_paginated': True
        })

    def test_paginated_list_last_page_specified(self):
        create_instance(quantity=30)
        view = ListView.as_view(model=Example, paginate_by=10)
        response = self.get(view, page='last')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['vanilla/example_list.html'])
        self.assertContext(response, {
            'object_list': Example.objects.all()[20:],
            'example_list': Example.objects.all()[20:],
            'view': InstanceOf(View),
            'page_obj': InstanceOf(Page),
            'paginator': InstanceOf(Paginator),
            'is_paginated': True
        })

    def test_paginated_list_invalid_page_specified(self):
        create_instance(quantity=30)
        view = ListView.as_view(model=Example, paginate_by=10)
        self.assertRaises(Http404, self.get, view, page=999)

    def test_paginated_list_non_integer_page_specified(self):
        create_instance(quantity=30)
        view = ListView.as_view(model=Example, paginate_by=10)
        self.assertRaises(Http404, self.get, view, page='null')


class TestCreate(BaseTestCase):
    def test_create(self):
        view = CreateView.as_view(model=Example, fields=('text',), success_url='/success/')
        response = self.post(view, data={'text': 'example'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/success/')
        self.assertEqual(Example.objects.count(), 1)
        self.assertEqual(Example.objects.get().text, 'example')

    def test_create_failed(self):
        view = CreateView.as_view(model=Example, fields=('text',), success_url='/success/')
        response = self.post(view, data={'text': 'example' * 100})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['vanilla/example_form.html'])
        self.assertFormError(response, 'form', 'text', ['Ensure this value has at most 10 characters (it has 700).'])
        self.assertContext(response, {
            'form': InstanceOf(BaseForm),
            'view': InstanceOf(View)
        })
        self.assertFalse(Example.objects.exists())

    def test_create_preview(self):
        view = CreateView.as_view(model=Example, fields=('text',), success_url='/success/')
        response = self.get(view)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['vanilla/example_form.html'])
        self.assertContext(response, {
            'form': InstanceOf(BaseForm),
            'view': InstanceOf(View)
        })
        self.assertFalse(Example.objects.exists())

    def test_create_no_success_url(self):
        view = CreateView.as_view(model=Example, fields=('text',))
        self.assertRaises(ImproperlyConfigured, self.post, view, data={'text': 'example'})

    def test_create_misconfigured_form_class(self):
        # If don't provide 'model' or 'form_class',
        # we should expect an ImproperlyConfigured exception.
        view = CreateView.as_view(
            queryset=Example.objects.all(),
            template_name='example.html',
            success_url='/success/'
        )
        self.assertRaises(ImproperlyConfigured, self.post, view, data={'text': 'example'})

    def test_create_create_no_fields(self):
        # If we don't provide `.fields` then expect a `PendingDeprecation` warning.
        view = CreateView.as_view(model=Example, success_url='/success/')
        self.assertRaises(ImproperlyConfigured, self.post, view, data={'text': 'example'})


class TestUpdate(BaseTestCase):
    def test_update(self):
        create_instance(quantity=3)
        pk = Example.objects.all()[0].pk
        view = UpdateView.as_view(model=Example, fields=('text',), success_url='/success/')
        response = self.post(view, pk=pk, data={'text': 'example'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/success/')
        self.assertEqual(Example.objects.count(), 3)
        self.assertEqual(Example.objects.get(pk=pk).text, 'example')

    def test_update_failed(self):
        create_instance(quantity=3)
        pk = Example.objects.all()[0].pk
        original_text = Example.objects.all()[0].text
        view = UpdateView.as_view(model=Example, fields=('text',), success_url='/success/')
        response = self.post(view, pk=pk, data={'text': 'example' * 100})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['vanilla/example_form.html'])
        self.assertFormError(response, 'form', 'text', ['Ensure this value has at most 10 characters (it has 700).'])
        self.assertContext(response, {
            'object': Example.objects.get(pk=pk),
            'example': Example.objects.get(pk=pk),
            'form': InstanceOf(BaseForm),
            'view': InstanceOf(View)
        })
        self.assertEqual(Example.objects.count(), 3)
        self.assertEqual(Example.objects.get(pk=pk).text, original_text)

    def test_update_preview(self):
        create_instance(quantity=3)
        pk = Example.objects.all()[0].pk
        view = UpdateView.as_view(model=Example, fields=('text',), success_url='/success/')
        response = self.get(view, pk=pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['vanilla/example_form.html'])
        self.assertContext(response, {
            'object': Example.objects.get(pk=pk),
            'example': Example.objects.get(pk=pk),
            'form': InstanceOf(BaseForm),
            'view': InstanceOf(View)
        })
        self.assertEqual(Example.objects.count(), 3)

    def test_update_no_success_url(self):
        create_instance(quantity=3)
        pk = Example.objects.all()[0].pk
        view = UpdateView.as_view(model=Example, fields=('text',))
        self.assertRaises(ImproperlyConfigured, self.post, view, pk=pk, data={'text': 'example'})

    def test_update_no_fields(self):
        # If we don't provide `.fields` then expect a `PendingDeprecation` warning.
        create_instance(quantity=3)
        pk = Example.objects.all()[0].pk
        view = UpdateView.as_view(model=Example, success_url='/success/')
        self.assertRaises(ImproperlyConfigured, self.post, view, pk=pk, data={'text': 'example'})


class TestDelete(BaseTestCase):
    def test_delete(self):
        create_instance(quantity=3)
        pk = Example.objects.all()[0].pk
        view = DeleteView.as_view(model=Example, success_url='/success/')
        response = self.post(view, pk=pk)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/success/')
        self.assertEqual(Example.objects.count(), 2)
        self.assertFalse(Example.objects.filter(pk=pk).exists())

    def test_delete_not_found(self):
        create_instance(quantity=3)
        view = DeleteView.as_view(model=Example, success_url='/success/')
        self.assertRaises(Http404, self.get, view, pk=999)

    def test_delete_preview(self):
        create_instance(quantity=3)
        pk = Example.objects.all()[0].pk
        view = DeleteView.as_view(model=Example, success_url='/success/')
        response = self.get(view, pk=pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['vanilla/example_confirm_delete.html'])
        self.assertContext(response, {
            'object': Example.objects.get(pk=pk),
            'example': Example.objects.get(pk=pk),
            'view': InstanceOf(View)
        })
        self.assertEqual(Example.objects.count(), 3)

    def test_delete_no_success_url(self):
        create_instance(quantity=3)
        pk = Example.objects.all()[0].pk
        view = DeleteView.as_view(model=Example)
        self.assertRaises(ImproperlyConfigured, self.post, view, pk=pk)


class TestAttributeOverrides(BaseTestCase):
    def test_template_name_override(self):
        create_instance(quantity=3)
        pk = Example.objects.all()[0].pk
        view = DetailView.as_view(model=Example, template_name='example.html')
        response = self.get(view, pk=pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['example.html'])
        self.assertContext(response, {
            'object': Example.objects.get(pk=pk),
            'example': Example.objects.get(pk=pk),
            'view': InstanceOf(View)
        })

    def test_template_name_suffix_override(self):
        create_instance(quantity=3)
        pk = Example.objects.all()[0].pk
        view = DetailView.as_view(model=Example, template_name_suffix='_suffix')
        response = self.get(view, pk=pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['vanilla/example_suffix.html'])
        self.assertContext(response, {
            'object': Example.objects.get(pk=pk),
            'example': Example.objects.get(pk=pk),
            'view': InstanceOf(View)
        })

    def test_context_object_name_override(self):
        create_instance(quantity=3)
        pk = Example.objects.all()[0].pk
        view = DetailView.as_view(model=Example, context_object_name='current')
        response = self.get(view, pk=pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['vanilla/example_detail.html'])
        self.assertContext(response, {
            'object': Example.objects.get(pk=pk),
            'current': Example.objects.get(pk=pk),
            'view': InstanceOf(View)
        })

    def test_form_class_override(self):
        class CustomForm(ModelForm):
            class Meta:
                fields = ('text',)
                model = Example
        view = CreateView.as_view(model=Example, success_url='/success/', form_class=CustomForm)
        response = self.get(view)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['vanilla/example_form.html'])
        self.assertContext(response, {
            'form': InstanceOf(CustomForm),
            'view': InstanceOf(View)
        })
        self.assertFalse(Example.objects.exists())

    def test_queryset_override(self):
        create_instance(text='abc', quantity=3)
        create_instance(text='def', quantity=3)
        view = ListView.as_view(model=Example, queryset=Example.objects.filter(text='abc'))
        response = self.get(view)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['vanilla/example_list.html'])
        self.assertContext(response, {
            'object_list': Example.objects.filter(text='abc'),
            'example_list': Example.objects.filter(text='abc'),
            'view': InstanceOf(View),
            'page_obj': None,
            'paginator': None,
            'is_paginated': False
        })


class TestTemplateView(BaseTestCase):
    def test_template_view(self):
        view = TemplateView.as_view(template_name='example.html')
        response = self.get(view)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['example.html'])
        self.assertContext(response, {
            'view': InstanceOf(View)
        })

    def test_misconfigured_template_view(self):
        # A template view with no `template_name` is improperly configured.
        view = TemplateView.as_view()
        self.assertRaises(ImproperlyConfigured, self.get, view)


class TestFormView(BaseTestCase):
    def test_form_success(self):
        view = FormView.as_view(
            form_class=ExampleForm,
            success_url='/success/',
            template_name='example.html'
        )
        response = self.post(view, data={'text': 'example'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/success/')

    def test_form_failure(self):
        view = FormView.as_view(
            form_class=ExampleForm,
            success_url='/success/',
            template_name='example.html'
        )
        response = self.post(view, data={'text': 'example' * 100})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['example.html'])
        self.assertFormError(response, 'form', 'text', ['Ensure this value has at most 10 characters (it has 700).'])
        self.assertContext(response, {
            'form': InstanceOf(BaseForm),
            'view': InstanceOf(View)
        })

    def test_form_preview(self):
        view = FormView.as_view(
            form_class=ExampleForm,
            success_url='/success/',
            template_name='example.html'
        )
        response = self.get(view)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['example.html'])
        self.assertContext(response, {
            'form': InstanceOf(BaseForm),
            'view': InstanceOf(View)
        })

    def test_misconfigured_form_view_no_form_class(self):
        # A template view with no `form_class` is improperly configured.
        view = FormView.as_view(
            success_url='/success/',
            template_name='example.html'
        )
        self.assertRaises(ImproperlyConfigured, self.get, view)

    def test_misconfigured_form_view_no_success_url(self):
        # A template view with no `success_url` is improperly configured.
        view = FormView.as_view(
            form_class=ExampleForm,
            template_name='example.html'
        )
        self.assertRaises(ImproperlyConfigured, self.post, view, data={'text': 'example'})
