django-model-timeline
=====================

Timeline view for Django models.

Quick start
-----------

1. install with pip

    pip install -e git://github.com/iterativ/django-model-timeline.git#egg=modeltimeline

2. Add "modeltimeline" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'django.contrib.humanize', # required
        'modeltimeline',
    )

3. Include the polls URLconf in your project urls.py like this::

    url(r'^admin/timeline/$', staff_member_required(TimeLine.as_view()), name='timeline'),

4. Visit http://127.0.0.1:8000/admin/timeline/ to see the timeline.


Hints
-----------
* Optimized for Bootstrap 3
* Requires Jquery