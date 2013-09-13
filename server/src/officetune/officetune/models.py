'''
Created on 13-09-2013

@author: kamil
'''
import uuid

from django.db import models, transaction
from django.contrib.auth.models import User


class Song(models.Model):
    
    name = models.CharField(max_length=2047)
    uid = models.CharField(max_length=511, default=lambda: unicode(int(uuid.uuid4())), blank=True)
    url = models.URLField(unique=True)
    votes_count = models.PositiveIntegerField(default=0, blank=True)
    played_today = models.BooleanField(default=False, blank=True)
    user = models.ForeignKey(User, related_name='songs')
    
    def __unicode__(self):
        return self.name
    

class Vote(models.Model):
    
    song = models.ForeignKey(Song, related_name='votes')
    user = models.ForeignKey(User, related_name='votes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        with transaction.commit_manually():
            self.song.votes_count += 1
            self.song.save()
            super(Vote, self).save(*args, **kwargs)
            transaction.commit()
    
    def delete(self, *args, **kwargs):
        with transaction.commit_manually():
            self.song.votes_count -= 1
            self.song.save()
            super(Vote, self).delete(*args, **kwargs)
            transaction.commit()