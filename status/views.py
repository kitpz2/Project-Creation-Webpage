#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Status
#       views.py
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


from svnweb.request.models import ProjectCreation
from django.shortcuts import render_to_response
from django.core import exceptions
from globals import check_premissions


def status(request):
    def errorHandle(error):
        return render_to_response('status.html', {
                'error' : error,
        })
    if !check_premissions('VC-HD-Access'):
        return HttpResponseRedirect("/request/")
    try:
        list_awaiting=ProjectCreation.objects.filter(status='awaiting_account')
        cmd=""
        all=""
        for account in list_awaiting:
            try:
                cmd="getent passwd " + account.libuser
                #all=all+cmd+"\n"
                #retrcode = call(cmd,shell=True)
                retrcode=system(cmd)
                if retrcode==0:
                    account.status="requested_repository"
                    account.save()
                else:
                    pass

            except OSError, e:
                error="Execution failed: "+ e
                return errorHandle(error)

        list_account=ProjectCreation.objects.filter(status='requested_account')
        list_repository=ProjectCreation.objects.filter(status='requested_repository')
        list_awaiting=ProjectCreation.objects.filter(status='awaiting_account')
        list_requested=ProjectCreation.objects.filter(status='requested')
        return render_to_response('status.html', {'list_account':list_account, 'list_repository':list_repository, 'list_awaiting':list_awaiting, 'list_requested':list_requested})

    except exceptions, e:
        error="Unable to access database: "+e
        return errorHandle(error)


