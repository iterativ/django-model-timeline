django-model-timeline
=====================

Timeline view for Django models.

Quick start
-----------

1. install with pip

    -e git://github.com/iterativ/django-model-timeline.git#egg=modeltimeline

2. Add "modeltimeline" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'modeltimeline',
    )

3. Include the polls URLconf in your project urls.py like this::

    url(r'^admin/modeltimeline/', include('polls.urls')),

4. Visit http://127.0.0.1:8000/admin/modeltimeline/ to see the timeline.