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
import bisect
import random


class NextSong(APIView):
    
    def get(self, request):
        since = datetime.now().replace(tzinfo=get_current_timezone())-timedelta(days=2)
        songs_with_votes = Song.objects.filter(votes_count__gt=0, votes__created_at__gt=since)
        not_yet_played = songs_with_votes.filter(played_today=False)
        if not_yet_played.count() == 0:
            songs_with_votes.update(played_today=False)
            not_yet_played = songs_with_votes.filter(played_today=False)
        try:
            chosen_song = weighted_random_choice(list(not_yet_played), lambda s: s.votes_count)
        except ValueError:
            return Response(data=None, status=404)
        chosen_song.played_today = True
        chosen_song.save()
        data = {
            'uid': chosen_song.uid,
            'url': chosen_song.url,
            'name': chosen_song.name,
        }
        
        return Response(data=data, status=200)


class DeleteSong(APIView):
    
    def delete(self, request, uid):
        Song.objects.filter(uid=uid).delete()
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
    
def weighted_random_choice(seq, weight):
    """Returns a random element from ``seq``. The probability for each element
    ``elem`` in ``seq`` to be selected is weighted by ``weight(elem)``.

    ``seq`` must be an iterable containing more than one element.

    ``weight`` must be a callable accepting one argument, and returning a
    non-negative number. If ``weight(elem)`` is zero, ``elem`` will not be
    considered. 
        
    """ 
    weights = 0
    elems = [] 
    for elem in seq:
        w = weight(elem)     
        try:
            is_neg = w < 0
        except TypeError:    
            raise ValueError("Weight of element '%s' is not a number (%s)" %
                             (elem, w))
        if is_neg:
            raise ValueError("Weight of element '%s' is negative (%s)" %
                             (elem, w))
        if w != 0:               
            try:
                weights += w
            except TypeError:
                raise ValueError("Weight of element '%s' is not a number "
                                 "(%s)" % (elem, w))
            elems.append((weights, elem))
    if not elems:
        raise ValueError("Empty sequence")
    ix = bisect.bisect(elems, (random.uniform(0, weights), None))
    return elems[ix][1]