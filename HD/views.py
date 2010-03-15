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


