# -*- coding: utf-8 -*-
#
# ITerativ GmbH
# http://www.iterativ.ch/
#
# Copyright (c) 16/09/14 ITerativ GmbH. All rights reserved.
#
# Created on 16/09/14
# @author: maersu
import datetime
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import ForeignKey, Q
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe
import pprint
from django_extensions.db.fields.json import JSONDict, JSONList

TL_IGNORE_FIELDS = getattr(settings, 'TL_IGNORE_FIELDS', ['password'])
TL_DEFAULT_FIELDS = getattr(settings, 'TL_DEFAULT_FIELDS', ['created'])
TL_DEFAULT_DAYS_BACKWARD = getattr(settings, 'TL_DEFAULT_DAYS_BACKWARD', 20)
TL_DEFAULT_DAYS_FORWARD = getattr(settings, 'TL_DEFAULT_DAYS_FORWARD', 20)
TL_ICON_FONT_CSS_URL = getattr(settings, 'TL_ICON_FONT_CSS_URL', '/static/glyphicons/css/glyphicons.css')

class TimeLiner(object):
    def __init__(self, start, end):
        self.start = datetime.datetime.combine(start, datetime.datetime.min.time())
        self.end = datetime.datetime.combine(end, datetime.datetime.max.time())
        self.today = datetime.date.today()

        self.entries = {}
        if self.is_in_time_range(datetime.datetime.combine(self.today, datetime.datetime.min.time())):
            self.entries[self.today] = {'entries': []}

        self.entity_cache = {}
        self.fields_cache = {}

    def add_time_stamped(self, klass, fields=None, icon=''):

        if fields is None:
            fields = TL_DEFAULT_FIELDS

        query = Q()
        for f in fields:
            query |= Q(**{'%s__range' % f: (self.start, self.end)})

        objects = klass.objects.filter(query)
        for o in objects:
            self.add_time_stamped_entity(o, fields, icon)

        return objects

    def is_in_time_range(self, date_time):
        return self.start <= date_time.replace(tzinfo=None) <= self.end

    def get_field_verbose_name(self, entity, field):

        key = entity.__class__.__name__

        if not key in self.fields_cache:
            model_cache = {}
            for f in entity.__class__._meta.fields:
                model_cache[f.name] = unicode(f.verbose_name).capitalize()

            self.fields_cache[key] = model_cache

        return self.fields_cache[key].get(field, field.capitalize())

    def add_time_stamped_entity(self, entity, fields, icon):

        use_cache = len(fields) > 1
        first = None

        for field in fields:
            adate = getattr(entity, field)

            if type(adate) == datetime.date:
                adate = datetime.datetime(adate.year, adate.month, adate.day)

            if adate:

                if first:
                    diff = adate - first
                    if (diff.days > 1):
                        self.add_entity(adate, entity, use_cache=use_cache, icon=icon,
                                        action=self.get_field_verbose_name(entity, field))

                else:
                    first = adate
                    self.add_entity(adate, entity, use_cache=use_cache, icon=icon,
                                    action=self.get_field_verbose_name(entity, field))

    def add_entity(self, entry_datetime, entity, url=None, icon=None, action=None, use_cache=False):

        if not self.is_in_time_range(entry_datetime):
            return {}

        name = unicode(entity.__class__._meta.verbose_name)
        klass = unicode(entity.__class__.__name__)

        date_key = entry_datetime.date()
        if not self.entries.has_key(date_key):
            self.entries[date_key] = {'entries': []}

        if use_cache:
            key = '%s-%s' % (klass, entity.id)
            if not self.entity_cache.has_key(key):
                dict_instance = dict_for_instance(entity)
                self.entity_cache[key] = dict_instance
            else:
                dict_instance = self.entity_cache[key]
        else:
            dict_instance = dict_for_instance(entity)

        self.entries[date_key]['entries'].append({'time': entry_datetime.time(),
                                                  'type': name,
                                                  'klass': klass,
                                                  'title': unicode(entity),
                                                  'dict': dict_instance,
                                                  'icon': icon,
                                                  'action': action,
                                                  'url': url})
        return dict_instance

    def initialize(self):
        self.iterator = iter(sorted(self.entries.iteritems(), reverse=True))

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.entries)

    def next(self):
        next = self.iterator.next()

        if next[0] < self.today:
            zone = 'past'
        elif next[0] > self.today:
            zone = 'future'
        else:
            zone = 'today'

        return (
            next[0], {'zone': zone, 'entries': sorted(next[1]['entries'], key=lambda tup: tup['time'])})


class DataFilterConfig(object):
    def __init__(self, data_config, used_timeline_filters=None):
        self.data_config = data_config
        self.iterator = iter(data_config)
        self.used_timeline_filters = used_timeline_filters

    def getVerboseName(self, klass):
        try:
            return unicode(klass._meta.verbose_name_plural)
        except:
            return self.getClassName(klass)

    def getClassName(self, klass):
        return unicode(klass.__name__)

    def __iter__(self):
        return self

    def next(self):
        next = self.iterator.next()
        klass = next['model']
        class_name = self.getClassName(klass)
        if self.used_timeline_filters:
            checked = (class_name in self.used_timeline_filters)
        else:
            checked = next.get('checked', True)

        next['class_name'] = class_name
        next['checked'] = checked
        next.setdefault('fields', TL_DEFAULT_FIELDS)
        next.setdefault('verbose_name', self.getVerboseName(klass))

        return next

    def get_start_date(self):
        return ''

    def get_end_date(self):
        return ''

    def parse_date(self, date_str):
        return datetime.date.today()


def dict_for_instance(instance):
    """Returns a dictionary for the given Django model instance with normalized data."""
    model = instance.__class__
    opts = model._meta
    data_map = SortedDict()
    suppress_object_id = False

    if not instance.pk:
        return {}

    if hasattr(instance, 'get_absolute_url'):
        data_map['Plattform'] = mark_safe('<a href="%(url)s">%(url)s</a>' % {'url': instance.get_absolute_url()})

    admin_url = reverse('admin:%s_%s_change' % (opts.app_label, model.__name__.lower()), args=[instance.pk])
    data_map['Admin'] = mark_safe('<a href="%(url)s">%(url)s</a>' % {'url': admin_url})

    for f in opts.fields:
        k = unicode(f.verbose_name).capitalize()

        if f.name in TL_IGNORE_FIELDS:
            continue

        v = getattr(instance, f.name)
        if hasattr(instance, 'get_%s_display' % f.name):
            m = getattr(instance, 'get_%s_display' % f.name)
            v = m()

        if type(f) == ForeignKey:
            try:
                to = f.related.parent_model
                if to == ContentType and f.name == 'content_type':
                    if hasattr(instance, 'object_id'):
                        try:
                            fobj = v.get_object_for_this_type(id=getattr(instance, 'object_id'))
                            text = '%s: %s' % (v, fobj)
                            if hasattr(fobj, 'get_absolute_url'):
                                text = mark_safe(
                                    '<a href="%(url)s">%(text)s</a>' % {'url': fobj.get_absolute_url(), 'text': text})
                            data_map['Content Object'] = text

                        except:
                            data_map['Content Object'] = ''
                            pass
                        suppress_object_id = True
                        continue
                else:
                    if v is not None:
                        klass = ContentType.objects.get_for_model(v)
                        text = '%s: %s' % (klass, v)

                        if hasattr(v, 'get_absolute_url'):
                            text = mark_safe(
                                '<a href="%(url)s">%(text)s</a>' % {'url': v.get_absolute_url(), 'text': text})

                        data_map[k] = text
                        continue

            except Exception, e:
                print e
                pass

        if v == None:
            v = ''
        elif type(v) == datetime.date:
            v = v.strftime("%d.%m.%Y")
        elif type(v) == datetime.datetime:
            v = v.strftime("%d.%m.%Y %H:%M")
        elif k.lower() == 'url' and v:
            v = mark_safe('<a href="%(url)s">%(url)s</a>' % {'url': v})
        elif isinstance(v, JSONDict):
            v = mark_safe(u'<pre>%s</pre>' % pprint.pformat(dict(v), indent=2))
        elif isinstance(v, JSONList):
            v = mark_safe(u'<pre>%s</pre>' % pprint.pformat(list(v), indent=2))

        data_map[k] = v

        if suppress_object_id and data_map.has_key('Object Id'):
            del data_map['Object Id']

    return data_map