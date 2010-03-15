# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class AuthGroup(models.Model):
    id = models.IntegerField(unique=True)
    name = models.CharField(unique=True, max_length=160, blank=True)
    class Meta:
        db_table = u'auth_group'

class AuthGroupPermissions(models.Model):
    id = models.IntegerField(unique=True)
    group_id = models.IntegerField(unique=True)
    permission_id = models.IntegerField(unique=True)
    class Meta:
        db_table = u'auth_group_permissions'

class AuthMessage(models.Model):
    id = models.IntegerField(unique=True)
    user_id = models.IntegerField()
    message = models.TextField(blank=True)
    class Meta:
        db_table = u'auth_message'

class AuthPermission(models.Model):
    id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    content_type_id = models.IntegerField(unique=True)
    codename = models.CharField(unique=True, max_length=200, blank=True)
    class Meta:
        db_table = u'auth_permission'

class AuthUser(models.Model):
    id = models.IntegerField(unique=True)
    username = models.CharField(unique=True, max_length=60, blank=True)
    first_name = models.CharField(max_length=60, blank=True)
    last_name = models.CharField(max_length=60, blank=True)
    email = models.CharField(max_length=150, blank=True)
    password = models.CharField(max_length=256, blank=True)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    is_superuser = models.IntegerField()
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    class Meta:
        db_table = u'auth_user'

class AuthUserGroups(models.Model):
    id = models.IntegerField(unique=True)
    user_id = models.IntegerField(unique=True)
    group_id = models.IntegerField(unique=True)
    class Meta:
        db_table = u'auth_user_groups'

class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(unique=True)
    user_id = models.IntegerField(unique=True)
    permission_id = models.IntegerField(unique=True)
    class Meta:
        db_table = u'auth_user_user_permissions'

class DjangoContentType(models.Model):
    id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200, blank=True)
    app_label = models.CharField(unique=True, max_length=200, blank=True)
    model = models.CharField(unique=True, max_length=200, blank=True)
    class Meta:
        db_table = u'django_content_type'

class DjangoSession(models.Model):
    session_key = models.CharField(max_length=80, primary_key=True)
    session_data = models.TextField(blank=True)
    expire_date = models.DateTimeField()
    class Meta:
        db_table = u'django_session'

class DjangoSite(models.Model):
    id = models.IntegerField(unique=True)
    domain = models.CharField(max_length=200, blank=True)
    name = models.CharField(max_length=100, blank=True)
    class Meta:
        db_table = u'django_site'

class Egroups(models.Model):
    username = models.CharField(unique=True, max_length=50)
    usergroup = models.CharField(unique=True, max_length=100)
    position = models.CharField(max_length=50, blank=True)
    class Meta:
        db_table = u'egroups'

class Position(models.Model):
    username = models.CharField(max_length=50, blank=True)
    usergroup = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=50, blank=True)
    class Meta:
        db_table = u'position'

class Project(models.Model):
    shortname = models.CharField(unique=True, max_length=20)
    libuser = models.CharField(max_length=20, blank=True)
    respuser = models.CharField(max_length=20, blank=True)
    longname = models.CharField(max_length=100, blank=True)
    respemail = models.CharField(max_length=60, blank=True)
    location = models.CharField(max_length=60, blank=True)
    restrictionlevel = models.CharField(max_length=20, blank=True)
    respname = models.CharField(max_length=60, blank=True)
    vc = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, blank=True)
    public_project = models.CharField(max_length=20, blank=True)
    class Meta:
        db_table = u'project'

class Projects(models.Model):
    vc = models.CharField(max_length=20, blank=True)
    shortname = models.CharField(max_length=100, blank=True)
    new_librarian = models.CharField(max_length=100, blank=True)
    size_new_quota = models.DecimalField(null=True, max_digits=0, decimal_places=-127, blank=True)
    class Meta:
        db_table = u'projects'

class ProjectCvs(models.Model):
    vc = models.CharField(max_length=50, blank=True)
    shortname = models.CharField(max_length=50, blank=True)
    longname = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=100, blank=True)
    restrictionlevel = models.CharField(max_length=20, blank=True)
    libuser = models.CharField(max_length=50, blank=True)
    respuser = models.CharField(max_length=50, blank=True)
    respemail = models.CharField(max_length=100, blank=True)
    respname = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=50, blank=True)
    migration = models.CharField(max_length=50, blank=True)
    migrationdate = models.CharField(max_length=50, blank=True)
    svnname = models.CharField(max_length=50, blank=True)
    comments = models.CharField(max_length=100, blank=True)
    id = models.DecimalField(null=True, max_digits=0, decimal_places=-127, blank=True)
    class Meta:
        db_table = u'project_cvs'

