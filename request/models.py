#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       models.py
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

from django.db import models
from django.forms import ModelForm

REP_CHOICES=(
	('R',"Restricted (only for a defined set of users)"),
	("C","CERN (for CERN users only)"),
	("W","World (available for everyone)"),
	)
	
REP_YESNO=(
	('yes',"Yes (Public)"),
	('no',"No (Private)"),
	)
	
	
class Project(models.Model):
	shortname=models.CharField(help_text="Short name for a project (max 20 chars)",max_length=20, primary_key=True)
	libuser=models.CharField(help_text="Librarian account ",max_length=20, blank=True)
	respuser=models.CharField(help_text="Username of somenone responsible for this project",max_length=20, blank=True)
	longname=models.CharField(help_text="Full name of repository",max_length=100)
	respemail=models.EmailField(help_text="Librarian e-mail",max_length=60, blank=True)
	location=models.CharField(help_text="Full Lcation in afs to the repository",max_length=60, blank=True)
	respname=models.CharField(help_text="Full name of somenone responsible for project",max_length=60)
	vc=models.CharField(help_text="Type of VC",max_length=20,default='svn')
	status=models.CharField(help_text="status of the repository",max_length=20, default='awaiting')
	restrictionlevel=models.CharField(help_text="Web and svn client read access should be",max_length=1, default="R", choices=REP_CHOICES)
	public_project=models.CharField(help_text="whether the project is public? yes/no",max_length=3,default='no', choices=REP_YESNO)
	class Meta:
		db_table = u'project'

class ProjectCreation(models.Model):
	longname=models.CharField(help_text="Full project name",max_length=100)
	shortname=models.CharField(help_text="Short project name",max_length=20, primary_key=True)
	requestorafs=models.CharField(help_text="Your AFS account", max_length=20)
	libuser=models.CharField(help_text="IF you want to use an existing librarian account, specify",max_length=20, blank=True)
	useradmin=models.CharField(help_text="Users to be given admin rights and write access:", max_length=256, blank=True)
	userwrite=models.CharField(help_text="Users to be given write access:", max_length=256, blank=True)
	userread=models.CharField(help_text="Users to be given read access:", max_length=256, blank=True)
	quota=models.CharField(help_text="Initial repository quota",max_length=4,default='500')
	personal=models.BooleanField(help_text="This repository will be my personal repository")
	status=models.CharField(help_text="status of the repsitory",max_length=20,default='requested', blank=True)#Sometimes Django losts value of this field, so to proper validation it's not needed to have value, but in views.py script checks if it has proper value and if not it adds it.
	use_existing_account=models.BooleanField(help_text="Use existing librarian account?", default=False)
	restrictionlevel=models.CharField(help_text="Web and svn client read access should be",max_length=1, default="R", choices=REP_CHOICES)
	password=models.CharField(help_text="Password for librarian account (minimum 8 letters)",max_length=128, blank=True)
class ProjectForm(ModelForm):
	class Meta:
		model=ProjectCreation
		
class ProjectMainForm(ModelForm):
	class Meta:
		model=Project
