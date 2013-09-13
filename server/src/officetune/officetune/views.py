'''
Created on 13-09-2013

@author: kamil
'''
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required

from rest_framework.views import APIView
from rest_framework.response import Response

from officetune.models import Song, Vote
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.utils.timezone import get_current_timezone
from officetune.forms import SongForm


class NextSong(APIView):
    
    def get(self, request):
        
        return Response(data={}, status=200)


class DeleteSong(APIView):
    
    def delete(self, request, uid):
        
        return Response(data=None, status=204)

@login_required
def song_list(request):
    
    songs = Song.objects.all()
    
    if request.method == "GET":
        return render_to_response(
            'officetune/song_list.html',
            {'songs': songs, 'song_form': SongForm()},
            context_instance=RequestContext(request)
        )
    
    if request.method == "POST":
        song_form = SongForm(request.POST)
        if song_form.is_valid():
            song = song_form.save(commit=False)
            song.user = request.user
            song.save()
            return redirect('song_list')
        else:
            return render_to_response(
                'officetune/song_list.html',
                {'songs': songs, 'song_form': song_form},
                context_instance=RequestContext(request),
            )

@login_required
def add_vote(request, song_id):
    
    if request.method == "POST":
        since = datetime.now().replace(tzinfo=get_current_timezone())-timedelta(days=1)
        user_votes_in_24 = Vote.objects.filter(user=request.user, created_at__gt=since).count()
        if user_votes_in_24 > 20: return redirect('no_more_votes')
        try:
            song = Song.objects.get(uid=song_id)
        except Song.DoesNotExist:
            return redirect('song_list')
        Vote.objects.create(user=request.user, song=song)
        return redirect('song_list')