#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
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
LOCATION="/afs/cern.ch/project/svn/usertest/reps/"
CreateHD="/afs/cern.ch/user/p/pzembrzu/create_project/scripts"
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


def index(request):
    def errorHandle(error, form):
        #form = ProjectForm()
        return render_to_response('index.html', {
                'error' : error,
                'form' : form,
        })
    if request.method == 'POST':
        form = ProjectForm(request.POST)

        if form.is_valid():
            if not form.cleaned_data['status']=='requested':
                form.cleaned_data['status']='requested'
            if not re.search("^[a-zA-Z0-9]+$",form.cleaned_data['shortname']):
                return errorHandle("Shortname can contain only letters and numbers", form)

            if (not form.cleaned_data['quota'].isdigit()) or ( int(form.cleaned_data['quota'])<50 or  int(form.cleaned_data['quota'])>1000):
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
                        return errorHandle("user "+user+" in 'useradmin' does not exists", form)

            if not len(form.cleaned_data['userwrite'])==0:
                users=form.cleaned_data['userwrite'].split(" ")
                for user in users:
                    if not check_user(user):
                        return errorHandle("user "+user+" in 'userwrite' does not exists", form)

            if not len(form.cleaned_data['userread'])==0:
                users=form.cleaned_data['userread'].split(" ")
                for user in users:
                    if not check_user(user):
                        return errorHandle("user "+user+" in 'userread' does not exists", form)

            if request.POST.getlist('condition'):

                form.cleaned_data['useradmin']=form.cleaned_data['useradmin'].strip()
                form.cleaned_data['useradmin']=replace(form.cleaned_data['useradmin']," ",":")

                form.cleaned_data['userread']=form.cleaned_data['userread'].strip()
                form.cleaned_data['userread']=replace(form.cleaned_data['userread']," ",":")

                form.cleaned_data['userwrite']=form.cleaned_data['userwrite'].strip()
                form.cleaned_data['userwrite']=replace(form.cleaned_data['userwrite']," ",":")

                form.save()
                subject="SVN: "+ form.cleaned_data['shortname']+" project requested (librarian: "+form.cleaned_data['requestorafs']+")"
                body="A new SVN repository for "+ form.cleaned_data['longname']+" was requested. In order to create it, go to:\n https://svnweb.cern.ch/admin/admin/create.php?status=requested&id=$id\n\n Once the librarian account is created, go to:\n https://svnweb.cern.ch/admin/admin/create.php?status=readytocreate-newaccount&id=$id\n\n Project creation Status board: https://svnweb.cern.ch/status/status.cgi\n\n"#stil old address
                creator=account+"@cern.ch"
                send_mail(subject, body, creator, [admins,helpdesk], fail_silently=False)

                subject="SVN: new project requested"
                body="This message is to confirm that you have requested a creation of a SVN repository for "+form.cleaned_data['longname']+". Once the repository is created, you will receive all necessary information by e-mail.\n\nIf you have any questions, send an e-mail to SVN.Support@cern.ch or consult the SVN Service web page: http://cern.ch/svn\n\nSVN Administators"
                mail=EmailMessage(subject, body, admins, [creator], headers = {'Reply-To': helpdesk})
                mail.send()

                return HttpResponse("<font color=\"green\"><b>Request sent to IT Help Desk.</b></font><p>")
            else:
                return errorHandle("You must agree to conditions", form)
        else:
            return errorHandle("Form is not Valid", form)
    else:
        form = ProjectForm()
        return render_to_response('index.html', {
            'form': form,
        })

def check_all_data(request, repo):
    def errorHandle(error, form):
        form = form
        return render_to_response('check_all_data.html', {
                'error' : error,
                'form' : form,
        })

    if request.method == 'POST':

    #try:
        tmp = ProjectCreation.objects.get(shortname=repo)
        form = ProjectForm(data = request.POST, instance = tmp)
    #except:
        #raise Http404
        if form.is_valid():
            '''tmp.longname=request.POST['longname']
            tmp.shortname=request.POST['shortname']
            tmp.requestorafs=request.POST['requestorafs']
            tmp.libuser=request.POST['libuser']
            tmp.useradmin=request.POST['useradmin']
            tmp.userwrite=request.POST['userwrite']
            tmp.userread=request.POST['userread']
            tmp.quota=request.POST['quota']
            if request.POST.getlist('personal'):
                tmp.personal=request.POST['personal']
            else:
                tmp.personal=False

            tmp.restrictionlevel=request.POST['restrictionlevel']

            if request.POST.getlist('use_existing_account'):
                tmp.use_existing_account=True
            else:
                tmp.use_existing_account=False'''

            if form.cleaned_data['use_existing_account']==True:#if user uses existing librarian
                form.cleaned_data['status']='requested_repository'#we don't need to create another one so we push project to 'create_repository'
                form.save()
                return HttpResponseRedirect("/request/"+tmp.shortname+"/create_repository/")
            else:
                form.cleaned_data['status']='requested_account'#if not we must first create a librarian account in 'create_librarian'
                form.save()
                return HttpResponseRedirect("/request/"+tmp.shortname+"/create_librarian/")
        else:
            errorHandle("Form is not valid",form)
    else:
        try:
            tmp = ProjectCreation.objects.get(shortname=repo)
        except:
            raise Http404

        form=ProjectForm(instance=tmp)
        #return errorHandle("OK!",{'form':form})
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
            #return errorHandle(command2,None)

            try:
                retrycode=popen("/afs/cern.ch/project/svn/dist/web/admin/run \""+command2+"\"")

            except OSError, e:
                error="Execution failed: "+ e
                return errorHandle(error)

            return errorHandle(command2+" :\n"+retrycode.readlines(),None)

            #return HttpResponseRedirect("/status/")



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



def status(request):
    def errorHandle(error):
        return render_to_response('status.html', {
                'error' : error,
        })

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






