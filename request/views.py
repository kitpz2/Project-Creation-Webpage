#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Request
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

from svnweb.request.models import ProjectForm, Project, ProjectCreation, ProjectMainForm
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, HttpResponseRedirect
from string import replace
import re
from django.core.mail import send_mail, EmailMessage
from django.core import exceptions
from os import system, popen

no_ldap=0
try:
    import ldap
except :
    no_ldap=1

admins="pzembrzu@cern.ch"
helpdesk="pzembrzu@cern.ch"
#helpdesk="helpdesk@cern.ch"

def check_user(user):
    if no_ldap==0:
        #l=ldap.open("ldap.cern.ch")
        l=ldap.open("ldap.cern.ch")
        baseDN="o=cern,c=ch"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        searchFilter = "UID="+user
        try:
            ldap_result_id = l.search(baseDN, searchScope, searchFilter, retrieveAttributes)
            exist=0
            while 1:
                result_type, result_data = l.result(ldap_result_id, 0)
                if (result_data == []):
                    break
                else:
                    ## here you don't have to append to a list
                    ## you could do whatever you want with the individual entry
                    ## The appending to list is just for illustration.
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        exist=exist+1
            if exist==1:
                return True
            else:
                return False
        except ldap.LDAPError, e:
            print e
    else:
        return True



def index(request):
    def errorHandle(error, form):
        #form = ProjectForm()
        return render_to_response('index.html', {
                'error' : error,
                'form' : form,
        })
    if request.method == 'POST':
        form = ProjectForm(request.POST)

        if form.is_valid(): #basic check

            if not form.cleaned_data['status']=='requested':
                form.cleaned_data['status']='requested'

            #more checks
            if not form.ValidateShortname():
                return errorHandle("Shortname can contain only letters and numbers", form)

            if not form.ValidateQuota():
                return errorHandle("quota must be a number between 50 and 10000 MB ", form)

            if not check_user(form.cleaned_data['requestorafs']):
                return errorHandle("user "+form.cleaned_data['requestorafs']+" does not exists", form)

            account=form.cleaned_data['requestorafs']

            if check_user(form.cleaned_data['libuser']):
                form.cleaned_data['use_existing_account']=True
            else:
                if form.cleaned_data['personal']==True:
                    form.cleaned_data['libuser']=form.cleaned_data['requestorafs']
                    form.cleaned_data['use_existing_account']=True
                else:
                    form.cleaned_data['libuser']=("lib"+form.cleaned_data['shortname'].lower())
                    form.cleaned_data['use_existing_account']=False

            try:
                if(Project.objects.get(shortname=form.cleaned_data['shortname'])):
                    return errorHandle("Repository with this shortname already exists", form)

            except Project.DoesNotExist:
                pass

            if not len(form.cleaned_data['useradmin'])==0:
                users=form.cleaned_data['useradmin'].split(" ")
                for user in users:
                    if not check_user(user):
                        return errorHandle("user "+user+" does not exist", form)

            if not len(form.cleaned_data['userwrite'])==0:
                users=form.cleaned_data['userwrite'].split(" ")
                for user in users:
                    if not check_user(user):
                        return errorHandle("user "+user+" does not exist", form)

            if not len(form.cleaned_data['userread'])==0:
                users=form.cleaned_data['userread'].split(" ")
                for user in users:
                    if not check_user(user):
                        return errorHandle("user "+user+" does not exist", form)

            if request.POST.getlist('condition'):

                form.cleaned_data['useradmin']=form.cleaned_data['useradmin'].strip()
                form.cleaned_data['useradmin']=replace(form.cleaned_data['useradmin']," ",":")

                form.cleaned_data['userread']=form.cleaned_data['userread'].strip()
                form.cleaned_data['userread']=replace(form.cleaned_data['userread']," ",":")

                form.cleaned_data['userwrite']=form.cleaned_data['userwrite'].strip()
                form.cleaned_data['userwrite']=replace(form.cleaned_data['userwrite']," ",":")

                form.save()
                #sending emails
                subject="SVN: "+ form.cleaned_data['shortname']+" project requested (librarian: "+form.cleaned_data['requestorafs']+")"
                body="A new SVN repository for "+ form.cleaned_data['longname']+" was requested. In order to create it, go to:\n https://svnweb.cern.ch/admin/admin/create.php?status=requested&id=$id\n\n Once the librarian account is created, go to:\n https://svnweb.cern.ch/admin/admin/create.php?status=readytocreate-newaccount&id=$id\n\n Project creation Status board: https://svnweb.cern.ch/status/status.cgi\n\n"#stil old address
                creator=account+"@cern.ch"
                response="<font color=\"green\"><b>Request sent to IT Help Desk.</b></font><p>"
                try:
                    send_mail(subject, body, creator, [admins,helpdesk], fail_silently=False)
                except:
                    response+="<br /> <font color=\"red\">Cannot send email to Help Desk</font>"

                subject="SVN: new project requested"
                body="This message is to confirm that you have requested a creation of a SVN repository for "+form.cleaned_data['longname']+". Once the repository is created, you will receive all necessary information by e-mail.\n\nIf you have any questions, send an e-mail to SVN.Support@cern.ch or consult the SVN Service web page: http://cern.ch/svn\n\nSVN Administators"
                mail=EmailMessage(subject, body, admins, [creator], headers = {'Reply-To': helpdesk})
                try:
                    mail.send()
                except:
                    response+="<br /> <font color=\"red\">Cannot send email to You</font>"

                return HttpResponse(response)
            else:
                return errorHandle("You must agree to conditions", form)
        else:
            return errorHandle("Form is not Valid", form)
    else:
        form = ProjectForm()
        return render_to_response('index.html', {
            'form': form,
        })




