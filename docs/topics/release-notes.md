# Release Notes

The `django-vanilla-views` package is not expected to change rapidly, as it's feature set is intended to remain in lock-step with Django's releases.

## Deprecation policy

The `django-vanilla-views` package follows a formal deprecation policy, which is in line with [Django's deprecation policy][django-deprecation-policy].

The timeline for deprecation of a feature present in version 1.0 would work as follows:

* Version 1.1 would remain **fully backwards compatible** with 1.0, but would raise `PendingDeprecationWarning` warnings if you use the feature that are due to be deprecated.  These warnings are **silent by default**, but can be explicitly enabled when you're ready to start migrating any required changes.  For example if you start running your tests using `python -Wd manage.py test`, you'll be warned of any API changes you need to make.

* Version 1.2 would escalate these warnings to `DeprecationWarning`, which is loud by default.

* Version 1.3 would remove the deprecated bits of API entirely.

## Upgrading

To upgrade `django-vanilla-views` to the latest version, use pip:

    pip install -U django-vanilla-views

You can determine your currently installed version using `pip freeze`:

    pip freeze | grep django-vanilla-views

---

## 2.0.0

**Released**: 10th September 2020

* Drop Python 2.7 and 3.4 support. Only Python 3.5+ is supported now.
* Support Django 3.1 (no compatibility changes were actually required).

## 1.1.0

**Released**: 15th June 2020

* Drop support for Django 1.8, 1.9, and 1.10.
* Support Django 2.2 and 3.0.

## 1.0.6

**Released**: 29th December 2018

* Support Django 2.1
* Don't throw warnings on any version of Django

## 1.0.5

**Released**: 23rd March 2018

* Update example to work with Django 1.8+
* Test on Django 1.8+
* Support Django 2.0

## 1.0.4

**Released**: 11th May 2015

* Support Django 1.7 and 1.8
* Support Python 3.4
* Fix error message in `get_success_url()`

## 1.0.3

**Released**: 22nd April 2014

* Add missing `*args`, `**kwargs` to `FormView.post()`

## 1.0.2

**Released**: 28th September 2013

* Resolve PyPI packaging issue.

## 1.0.1

**Released**: 24th September 2013

* Fix `DeleteView.template_name_suffix` by changing it to `'_confirm_delete'`.

## 1.0.0

**Released**: 23rd September 2013

* Introduced `get_success_url()` for easier mixin overriding of view behavior.
* Introduced `**kwargs` arguments to `get_form` to kee API identical between base and model views, and for easier mixin overriding.
* Introduced 1.6's behavior of pending deprecation for `.fields` not specified when auto-generating model forms.

## 0.2.1

**Released**: 10th September 2013

* **Beta release.**
* Fix method names to match Django's.

## 0.2.0

**Released**: 9th September 2013

* Fix some messaging.
* Python 3 compatibility.
* Use Django's `RedirectView`.

## 0.1.2

**Released**: 7th September 2013

* Simple module names.
* Refactored pagination.

## 0.1.1

**Released**: 2nd September 2013

* Fix missing arguments.

## 0.1.0

**Released**: 2nd September 2013

* **Alpha release.**

[django-deprecation-policy]: https://docs.djangoproject.com/en/dev/internals/release-process/#internal-release-deprecation-policy
