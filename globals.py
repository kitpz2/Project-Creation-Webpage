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

SVNMAIN="/afs/cern.ch/project/svn/usertest/"
LOGS=SVNMAIN+"logs/"
LOCATION=SVNMAIN+"reps/"
CreateHD=SVNMAIN+"scripts/repo/createHD.sh"
admins="pzembrzu@cern.ch"
helpdesk="pzembrzu@cern.ch"
#helpdesk="helpdesk@cern.ch"

def check_premissions(request,who):
    try:
        groups=request.META['ADFS_GROUP'].split(';')
        for group in groups:
            if group == who:
                access=True
        if access==False:
            return False
        else:
            return True
    except:
        return False
