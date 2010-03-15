		try:
			tmp = ProjectCreation.objects.get(shortname=repo)
		except:
			raise Http404
		
		form=ProjectForm(instance=tmp)
		if form.is_valid():
			form.cleaned_data['longname']=request.POST['longname']
			form.cleaned_data['shortname']=request.POST['shortname']
			form.cleaned_data['requestorafs']=request.POST['requestorafs']
			form.cleaned_data['libuser']=request.POST['libuser']
			form.cleaned_data['useradmin']=request.POST['useradmin']
			form.cleaned_data['userwrite']=request.POST['userwrite']
			form.cleaned_data['userread']=request.POST['userread']
			form.cleaned_data['quota']=request.POST['quota']
			form.cleaned_data['personal']=request.POST['personal']
			form.cleaned_data['restrictionlevel']=request.POST['restrictionlevel']
			form.cleaned_data['use_existing_account']=request.POST['use_existing_account']
			if form.cleaned_data['use_existing_account']==True:
				form.cleaned_data['restrictionlevel']="requested_repository"
			else:
				form.cleaned_data['restrictionlevel']="requested_account"
			if form.is_valid(): 
				if form.cleaned_data['use_existing_account']==True:#if user uses existing librarian
					form.cleaned_data['status']='requested_repository'#we don't need to create another one so we push project to 'create_repository'
					form.save()
					return HttpResponseRedirect("/request/"+form.cleaned_data['shortname']+"/create_repository/")
				else:
					form.cleaned_data['status']='requested_account'#if not we must first create a librarian account in 'create_librarian'
					form.save()
					return HttpResponseRedirect("/request/"+form.cleaned_data['shortname']+"/create_librarian/")
			else:
				return errorHandle("Form is not valid2!",{'form':form})
				
				
try:
	retrcode = call("getent passwd " + "pzembr;zuj",shell=True)
	if retrcode<0:
		print "child was terminated by signal",-retrcode
	else:
		print "child returned", retrcode
except:
	print "blad"
