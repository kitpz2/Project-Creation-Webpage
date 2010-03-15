from svnweb.request.models import Project
from django.contrib import admin

#
class ProjectAdmin(admin.ModelAdmin):
		fields = ['shortname', 'longname', 'libuser', 'respname',
		'respuser', 'respemail', 'location', 'restrictionlevel', 
		'vc', 'status', 'public_project']
		list_display=('shortname','libuser', 'respuser', 'vc', 'status', 'public_project')
		list_filter=['public_project', 'vc', 'status']
		search_fields=['shortname','libuser','respuser']
		
admin.site.register(Project, ProjectAdmin)
