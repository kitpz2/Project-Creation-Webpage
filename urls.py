#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       urls.py
#
#       Copyright 2010 Paweł Zembrzuski <pawel.zembrzuski@cern.ch>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^svnweb/', include('svnweb.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^request/$','svnweb.request.views.index'),
     (r'^status/$','svnweb.status.views.status'),
     (r'^HD/(?P<repo>[a-zA-Z0-9-]+)/create_librarian/$','svnweb.HD.views.create_librarian'),
     (r'^HD/(?P<repo>[a-zA-Z0-9-]+)/create_account/$','svnweb.HD.views.create_librarian'),
     (r'^HD/(?P<repo>[a-zA-Z0-9-]+)/check_account/$','svnweb.HD.views.check_all_data'),
     (r'^HD/(?P<repo>[a-zA-Z0-9-]+)/create_repository/$','svnweb.HD.views.create_repository'),
     (r'^HD/(?P<repo>[a-zA-Z0-9-]+)/waiting/$','svnweb.HD.views.waiting'),

     #(r'^(
     (r'^admin/', include(admin.site.urls)),
     (r'^request/css/(?P<path>.*)$', 'django.views.static.serve',{'document_root': 'request/css/'}),
     (r'^request/media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': 'request/media/'}),
)
