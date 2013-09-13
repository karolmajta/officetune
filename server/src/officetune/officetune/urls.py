from django.conf.urls import patterns, include, url
import django.contrib.auth.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.generic.base import TemplateView
admin.autodiscover()

import officetune.views


urlpatterns = patterns('',
    url(r'^login/$',
        django.contrib.auth.views.login,
        {'template_name': 'officetune/login.html'},
        name='login'),
    url(r'^logout/$',
        django.contrib.auth.views.logout,
        {'next_page': '/'},
        name='logout'),
    url(r'^$',
        officetune.views.song_list,
        name='song_list'),
    url(r'^vote/(?P<song_id>\d+)$',
        officetune.views.add_vote,
        name='add_vote'),
    url(r'^too-many-votes/$',
        TemplateView.as_view(template_name='officetune/too-many-votes.html'),
        name='no_more_votes'),
                       
    url(r'^api/next$',
        officetune.views.NextSong.as_view(),
    ),
                       
    url(r'^api/songs/(?P<uid>\d+)$',
        officetune.views.DeleteSong.as_view(),
    ),

    url(r'^admin/', include(admin.site.urls)),
)
