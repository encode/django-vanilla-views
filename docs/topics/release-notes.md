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

## 1.0.0

**Released**: **PENDING**

[django-deprecation-policy]: https://docs.djangoproject.com/en/dev/internals/release-process/#internal-release-deprecation-policy
