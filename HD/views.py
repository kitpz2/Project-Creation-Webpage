#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       HD
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
from subprocess import Popen
from django.conf import settings
from globals import SVNMAIN, LOGS, LOCATION, CreateHD

no_ldap=0
try:
    import ldap
except :
    no_ldap=1

def check_user_data(user):
    if no_ldap==0:
        l=ldap.open("ldap.cern.ch")
        baseDN="o=cern,c=ch"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ['mail','displayName',]
        searchFilter = "UID="+user
        person=0
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
                        person=result_data
            if exist==1:
                return person
            else:
                return False
        except ldap.LDAPError, e:
            print e
    else:
        return False


def check_all_data(request, repo):
    def errorHandle(error, form):
        form = form
        return render_to_response('check_all_data.html', {
                'error' : error,
                'form' : form,
        })

    if request.method == 'POST':

        try:
            tmp = ProjectCreation.objects.get(shortname=repo)
            form = ProjectForm(data = request.POST, instance = tmp)
        except:
            raise Http404

        if form.is_valid():
            if form.cleaned_data['use_existing_account']==True:#if user uses existing librarian
                form.cleaned_data['status']='requested_repository'#we don't need to create another one so we push project to 'create_repository'
                form.save()
                return HttpResponseRedirect("/HD/"+tmp.shortname+"/create_repository/")
            else:
                form.cleaned_data['status']='requested_account'#if not we must first create a librarian account in 'create_librarian'
                form.save()
                return HttpResponseRedirect("/HD/"+tmp.shortname+"/create_librarian/")
        else:
            errorHandle("Form is not valid",form)
    else:
        try:
            tmp = ProjectCreation.objects.get(shortname=repo)
        except:
            raise Http404

        form=ProjectForm(instance=tmp)
        if tmp.status=="requested":
            return render_to_response('check_all_data.html', {'form':form})
        elif tmp.status=="requested_repository":
            return errorHandle("Account created. go to status page!", None)
        elif tmp.status=="awaiting_account":
            return errorHandle("Awaiting for account!", None)
        elif tmp.status=="active":
            return errorHandle("Repository already created and active!", None)
        else:
            return errorHandle("Unknown status of this repository", None)

def create_librarian(request, repo):
    def errorHandle(error,login):
        return render_to_response('create_account.html', {
                'error' : error,
                'login' : login,
        })

    if request.method == 'POST':
        try:
            tmp = ProjectCreation.objects.get(shortname=repo)
        except :
            raise Http404

        account_name=request.POST['login']
        passwd=request.POST['password']
        if len(passwd)<8:
            return errorHandle("Password is to short",tmp.libuser)
        tmp.libuser=account_name
        tmp.password=passwd
        tmp.status="awaiting_account"
        tmp.save()
        return HttpResponseRedirect("/ status/")

    else:
        try:
            tmp = ProjectCreation.objects.get(shortname=repo)
        except :
            raise Http404
        #form=ProjectForm(instance=tmp)
        if tmp.use_existing_account==True:
            empty=ProjectForm()
            return errorHandle("Repository "+tmp.longname+" ("+tmp.shortname+") have existing librarian account already2",empty)
        else:
            if tmp.status=="requested_account":
                return render_to_response('create_account.html', {'login': tmp.libuser})
            elif tmp.status=="requested_repository":
                return errorHandle("Account created. go to status page!", None)
            elif tmp.status=="awaiting_account":
                return errorHandle("Awaiting for account!", None)
            elif tmp.status=="active":
                return errorHandle("Repository already created and active!", None)
            else:
                return errorHandle("Unknown status of this repository", None)

def create_repository(request, repo):
    def errorHandle(error,form):
        return render_to_response('create_repository.html', {
                'error' : error,
                'form' : form,
        })

    if request.method == 'POST':
        form = ProjectMainForm(request.POST)
        if form.is_valid():
            form.cleaned_data['status']="active"
            try:
                tmp = ProjectCreation.objects.get(shortname=form.cleaned_data['shortname'])
            except :
                raise Http404
            tmp.status=form.cleaned_data['status']
            realQuota=int(tmp.quota)*1024

            form.save()
            tmp.save()
            pers=""
            if tmp.personal==True:
                pers="yes"
            else:
                pers="no"
            use_existing=""
            if tmp.use_existing_account==True:
                use_existing="yes"
            else:
                use_existing="no"

            #executing script:
            command2 ="cd "+ CreateHD + "; ./create-projectHD.sh " + form.cleaned_data['shortname'] +' \''+ form.cleaned_data['longname'] +'\' \''+ form.cleaned_data['respuser'] +'\' \''+ form.cleaned_data['respemail'] +'\' \''+ form.cleaned_data['libuser'] +'\' \''+ tmp.userwrite +'\' \''+ tmp.password +'\' \''+ form.cleaned_data['restrictionlevel'] +'\' \''+ tmp.useradmin +'\' \''+ tmp.userread +'\' \''+ pers +'\' \''+ str(realQuota)+'\''
            out=open(LOGS+tmp.shortname+"-ProjectCreation.log","w")
            err=open(LOGS+tmp.shortname+"-ProjectCreationErrors.log","w")
            try:
                if settings.DEBUG:
                    pass
                else:
                    Popen("/afs/cern.ch/project/svn/dist/web/admin/run \""+command2+"\"", stdout=out, stderr=err)
            except OSError, e:
                error="Execution failed: "+ e
                return errorHandle(error)

            return HttpResponseRedirect("/HD/"+tmp.shortname+"/waiting/")

        else:
            return errorHandle("Form is not Valid", form)
    else:
        try:
            tmp = ProjectCreation.objects.get(shortname=repo)
        except :
            raise Http404
        if tmp.status=="requested_repository":
            location=LOCATION+tmp.shortname.lower()+"/"
            respemail=check_user_data(tmp.requestorafs)[0][1]['mail'][0]
            respname=check_user_data(tmp.requestorafs)[0][1]['displayName'][0]

            form=ProjectMainForm(initial={
                'shortname':tmp.shortname,
                'libuser':tmp.libuser,
                'respuser':tmp.requestorafs,
                'longname':tmp.longname,
                'respemail':respemail,
                'location':location,
                'restrictionlevel':tmp.restrictionlevel,
                'respname':respname,
                'status':tmp.status,

                })
            for field in form:
                field.field.widget.attrs['readonly']=None

            return render_to_response('create_repository.html', {'form': form})
        else:
            if tmp.status=="requested_account":
                return errorHandle("First create libraian account for <a href=\"/request/"+tmp.shortname+"/create_librarian/\">this repository</a>", {'form': form})
            elif tmp.status=="awaiting_account":
                return errorHandle("Awaiting for account!", None)
            elif tmp.status=="active":
                return errorHandle("Repository already created and active!",  None)
            else:
                return errorHandle("Unknown status of this repository",None)

def waiting(request, repo):
    out_str=""
    err_str=""
    try:
        out=open(LOGS+tmp.shortname+"-ProjectCreation.log","w")
        out_str=out.read()
    except:
        out_str="Cannot open Log"

    try:
        err=open(LOGS+tmp.shortname+"-ProjectCreationErrors.log","w")
        err_str=out.read()
    except:
        err_str="Cannot open Error Log"

    return render_to_response('create_repository.html', {'out_str': out_str, "err_str":err_str})
