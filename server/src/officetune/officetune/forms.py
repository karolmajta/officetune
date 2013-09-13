'''
Created on 13-09-2013

@author: kamil
'''
from django import forms
from officetune.models import Song

class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ('name', 'url')