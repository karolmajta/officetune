'''
Created on 13-09-2013

@author: kamil
'''
from django.contrib import admin

from officetune.models import Song, Vote

admin.site.register(Vote)
admin.site.register(Song)

