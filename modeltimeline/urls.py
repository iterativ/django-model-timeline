# -*- coding: utf-8 -*-
#
# ITerativ GmbH
# http://www.iterativ.ch/
#
# Copyright (c) 2013 ITerativ GmbH. All rights reserved.
#
# Created on Nov 28, 2013
# @author: maersu <me@maersu.ch>
from modeltimeline.views import TimeLineContent, TimeLineIndex

from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import TemplateView

urlpatterns = patterns('',
                       url(r'^$', staff_member_required(TimeLineIndex.as_view()),
                           name='timeline_index'),
                       url(r'^content/$', staff_member_required(TimeLineContent.as_view()), name="timeline_content"),
)
