from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.conf import settings

from django.contrib import admin
admin.autodiscover() 

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'blog.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^blog/index$', 'blog.views.index', name='index'),
    url(r'^blog$', 'blog.views.home', name='home'),
    
    url(r'^blog/add-item$', 'blog.views.add_item', name='add-item'),
    url(r'^blog/edit-item/(?P<item_id>\d+)$', 'blog.views.edit_item', name='edit-item'),
    url(r'^blog/delete-item/(?P<item_id>\d+)$', 'blog.views.delete_item', name='delete_event'),

    # Route for built-in authentication with our own custom login page
    url(r'^blog/manage$', 'blog.views.manage', name='manage'),

    # Route for built-in authentication with our own custom login page
    url(r'^blog/login$', 'blog.views.login_attempt', name='login'),

    # Route to loguout a user and send them back to the login page
    url('^blog/logout$', 'blog.views.logout_view', name='logout'),
    
    # Route for registering users
    url(r'^blog/register$', 'blog.views.register', name='register'),

    # Route for confirming users
    url(r'^blog/confirm', 'blog.views.confirm', name='confirm'),

    url(r'^blog/get-userlist$', 'blog.views.get_userlist', name='get-userlist'),
    url(r'^blog/user/(?P<username>\S+)$', 'blog.views.get_user', name='get-user'),

    url(r'^blog/get-eventlist$', 'blog.views.get_eventlist', name='get-eventlist'),
    url(r'^blog/get-user-eventlist$', 'blog.views.get_user_eventlist', name='get-eventlist'),

    url(r'^blog/event/(?P<city>\w+)/(?P<state>\w+)$', 'blog.views.get_events_by_location', name='get-eventlist'),

    url(r'^blog/photo/(?P<id>\d+)$', 'blog.views.get_photo', name='photo'),
    
    url(r'^blog/event/(?P<id>\d+)$', 'blog.views.get_event', name='get-event'),
    url(r'^blog/rsvp/(?P<event_id>\d+)/(?P<rsvp_choice>[J,M,D])$', 'blog.views.new_rsvp_event', name='new_rsvp_event'),

    url(r'^blog/rsvp-user/(?P<event_id>\d+)$', 'blog.views.get_event_rsvp_user', name='get_rsvp_event_user'),

)
