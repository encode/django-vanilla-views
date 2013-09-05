from django.core.paginator import Page, Paginator
from django.db import models
from django.forms import BaseForm, ModelForm
from django.http import Http404
from django.test import RequestFactory, TestCase
from model_mommy import mommy
from vanilla import CreateView, DetailView, DeleteView, ListView, UpdateView, View
import types


class Example(models.Model):
    text = models.CharField(max_length=10)

    class Meta:
        ordering = ('id',)


class InstanceOf(object):
    """
    We use this sential object together with our 'assertContext' helper method.

    Used to ensure that a particular context value is an object of the given
    type, without requiring a specific fixed value.  Useful for form context,
    and other complex instances.
    """
    def __init__(self, expected_type):
        self.expected_type = expected_type


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
        mommy.make(Example, _quantity=3)
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
        mommy.make(Example, _quantity=3)
        view = DetailView.as_view(model=Example)
        self.assertRaises(Http404, self.get, view, pk=999)


class TestList(BaseTestCase):
    def test_list(self):
        mommy.make(Example, _quantity=3)
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
        mommy.make(Example, _quantity=25)
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
        mommy.make(Example, _quantity=25)
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
        mommy.make(Example, _quantity=25)
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
        mommy.make(Example, _quantity=25)
        view = ListView.as_view(model=Example, paginate_by=10)
        self.assertRaises(Http404, self.get, view, page=999)

    def test_paginated_list_non_integer_page_specified(self):
        mommy.make(Example, _quantity=25)
        view = ListView.as_view(model=Example, paginate_by=10)
        self.assertRaises(Http404, self.get, view, page='null')


class TestCreate(BaseTestCase):
    def test_create(self):
        view = CreateView.as_view(model=Example, success_url='/success/')
        response = self.post(view, data={'text': 'example'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/success/')
        self.assertEqual(Example.objects.count(), 1)
        self.assertEqual(Example.objects.get().text, 'example')

    def test_create_failed(self):
        view = CreateView.as_view(model=Example, success_url='/success/')
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
        view = CreateView.as_view(model=Example, success_url='/success/')
        response = self.get(view)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['vanilla/example_form.html'])
        self.assertContext(response, {
            'form': InstanceOf(BaseForm),
            'view': InstanceOf(View)
        })
        self.assertFalse(Example.objects.exists())


class TestUpdate(BaseTestCase):
    def test_update(self):
        mommy.make(Example, _quantity=3)
        pk = Example.objects.all()[0].pk
        view = UpdateView.as_view(model=Example, success_url='/success/')
        response = self.post(view, pk=pk, data={'text': 'example'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/success/')
        self.assertEqual(Example.objects.count(), 3)
        self.assertEqual(Example.objects.get(pk=pk).text, 'example')

    def test_update_failed(self):
        mommy.make(Example, _quantity=3)
        pk = Example.objects.all()[0].pk
        original_text = Example.objects.all()[0].text
        view = UpdateView.as_view(model=Example, success_url='/success/')
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
        mommy.make(Example, _quantity=3)
        pk = Example.objects.all()[0].pk
        view = UpdateView.as_view(model=Example, success_url='/success/')
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


class TestDelete(BaseTestCase):
    def test_delete(self):
        mommy.make(Example, _quantity=3)
        pk = Example.objects.all()[0].pk
        view = DeleteView.as_view(model=Example, success_url='/success/')
        response = self.post(view, pk=pk)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/success/')
        self.assertEqual(Example.objects.count(), 2)
        self.assertFalse(Example.objects.filter(pk=pk).exists())

    def test_delete_not_found(self):
        mommy.make(Example, _quantity=3)
        view = DeleteView.as_view(model=Example, success_url='/success/')
        self.assertRaises(Http404, self.get, view, pk=999)

    def test_delete_preview(self):
        mommy.make(Example, _quantity=3)
        pk = Example.objects.all()[0].pk
        view = DeleteView.as_view(model=Example, success_url='/success/')
        response = self.get(view, pk=pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['vanilla/example_detail.html'])
        self.assertContext(response, {
            'object': Example.objects.get(pk=pk),
            'example': Example.objects.get(pk=pk),
            'view': InstanceOf(View)
        })
        self.assertEqual(Example.objects.count(), 3)


class TestAttributeOverrides(BaseTestCase):
    def test_template_name_override(self):
        mommy.make(Example, _quantity=3)
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
        mommy.make(Example, _quantity=3)
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
        mommy.make(Example, _quantity=3)
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
        mommy.make(Example, text='abc', _quantity=3)
        mommy.make(Example, text='def', _quantity=3)
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