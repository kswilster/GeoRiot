from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist

# Decorator to use built-in authenitcation system
from django.contrib.auth.decorators import login_required

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout

# Needed to manually create HttpResponses or raise an Http404 exception
from django.http import HttpResponse, Http404

#For json responses
import json
from django.core import serializers

# For email sending
from django.core.mail import send_mail

# Helper function to guess a MIME type from a file name
from mimetypes import guess_type

from blog.models import * 
from blog.forms import *

from django.contrib import messages
from django.db import transaction

import random, string, datetime
from datetime import date, time, datetime

#For handling json responses
def json_response(x):
    return HttpResponse(json.dumps(x, sort_keys=True, indent=2),
                        content_type='application/json; charset=UTF-8')

def index(request):
    context = {}
    context['register'] = RegistrationForm()
    context['addevent'] = EventForm()

    return render(request, 'home.html', context)

def home(request):
    #Sets up a list of blogposts that people have
    context = { 'users' : User.objects.order_by('username') }
    dt = datetime.now()
    print dt
    context['date_cur'] = dt.date()
    context['time_cur'] = dt.time()

    if request.method == "GET":
        # IF authenticated, grab blog posts that user is following
        if request.user.is_authenticated():
            u_prof = UserProfile.objects.get(user=request.user)
            
            fol_users = u_prof.fol_users
            list_fol = fol_users.split(",")
            user_list = []
            for user_fol in list_fol[1:]:
                user_list.append(User.objects.get(username=user_fol))

            context['events'] = Event.get_posts_ul(user_list)
            context['fol_users'] = list_fol[1:]
            print context
	    return render(request, 'index.html', context)

        # If not authenticated, then grab all blogposts
	context['events'] = Event.objects.order_by('-date_start')
	return render(request, 'index.html', context)

    # Not logged in and POST
    if not request.user.is_authenticated():
	username = request.POST['req_user']
	if username:
	    user = User.objects.get(username=username)
	    context['events'] = Event.objects.filter(user=user).order_by('-date_start')
            # To keep track of the one user that anonymous peple can view at a time
            context['fol_user'] = username
	else:
	    context['events'] = Event.objects.order_by('-date_start')

	return render(request, 'index.html', context)

    # Logged in and POST
    username = request.POST['req_user']
    # Create the list of following users and make them join/fall off depending 
    # on their current status
    u_prof = UserProfile.objects.get(user=request.user)
    fol_users = u_prof.fol_users
    list_fol = fol_users.split(",")
    if username in list_fol:
        list_fol.remove(username)
        list_fol.sort()
        fol_users = string.join(list_fol, ",")
    else:
        list_fol.append(username)
        list_fol.sort()
        fol_users = string.join(list_fol, ",")

    u_prof.fol_users = fol_users
    u_prof.save()

    user_list = []
    for user_fol in list_fol[1:]:
        user_list.append(User.objects.get(username=user_fol))

    context['events'] = Event.get_posts_ul(user_list)
    context['fol_users'] = list_fol[1:]
    return render(request, 'index.html', context)

# Manages the current user's blog posts
@login_required
def manage(request):
    context = {}
    errors = []
    context['events'] = reversed(Event.get_posts(request.user))
    context['manage'] = True
    
    return render(request, 'index.html', context)

@login_required
def add_item(request):
    errors = []
    context = {}

    if request.method == "GET":
        context = {'form':EventForm()}
	return render(request, 'add-entry.html', context)

    new_event = Event(user=request.user)
    form = EventForm(request.POST, request.FILES, instance=new_event)

    # Creates a new item if it is present as a parameter in the request
    if not form.is_valid():
        form = EventForm(request.POST)
        context['form'] = form
        print "i'm not happy for some reason???"
        return render(request, 'add-entry.html', context)

    form.save()
    context['errors'] = errors
    context['form'] = EventForm()
    return render(request, 'add-entry.html', context)

# Code to delete an event from the list. Only the owner of the event can delete
# their own events
@login_required
def delete_item(request, item_id):
    errors = []
    context = {}

    try:
        event_to_delete = Event.objects.get(id=item_id)
        if (event_to_delete.user == request.user):
            event_to_delete.delete()
        else:
            print "Error with deleting stuff"
            messages.add_message(request, messages.ERROR, "You do not have permission to delete this event")

    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, 'The event you were looking for does not exist')
    
    return redirect(reverse('manage'))

# Edit an event.  Only the owner of the event can edit their own events
@login_required
@transaction.atomic
def edit_item(request, item_id):
    event_to_edit = get_object_or_404(Event, user=request.user, id=item_id)
    
    if request.method == 'GET':
        form = EventForm(instance=event_to_edit)
        context = {'form':form}
        return render(request, 'add-entry.html', context)

    form = EventForm(request.POST, instance=event_to_edit)
    
    if not form.is_valid():
        context = {'form':form}
        return render(request, 'add-entry.html', context)
         
    form.save()
    return redirect(reverse('manage'))

# Returns the event based on ID with the xml file.
def get_event(request, id):
    content = {}
    event_got = get_object_or_404(Event, id = id)
    rsvps = RsvpEvent.objects.filter(event = event_got)

    if event_got.picture:
        picture_url = reverse('photo', kwargs={'id':id})
        content['picture'] = picture_url
    
    content['event'] = event_got
    content['rsvps'] = rsvps

    return render(request, 'event.xml', content, content_type='application/xml')
    """return json_response({
        'event' : serializers.serialize
        'rsvps' : serializers.serialize('json', rsvps)
    })"""

def get_events_by_location(request, city, state):
    content = {}
    content['events'] = Event.objects.filter(city=city, state=state)

    return render(request, 'eventlist.xml', content, content_type='application/xml');

@login_required
@transaction.atomic
def new_rsvp_event(request, event_id, rsvp_choice):
    context = {}
    user_prof = UserProfile.objects.get(user=request.user)
    event = get_object_or_404(Event, id=event_id)

    try: 
        rsvp = RsvpEvent.objects.get(userProfile=user_prof, event=event)
    except ObjectDoesNotExist:
        rsvp = None

    # If there is already an RSVP event, edit that event rather than making anew one
    if (rsvp):
        if (rsvp_choice == 'J'):
            rsvp.rsvp_choice='J'
        elif (rsvp_choice == 'M'):
            rsvp.rsvp_choice='M'
        else:
            rsvp.rsvp_choice='D'
        rsvp.save()
        return json_response({
          'success': True
        })

    # Otherwise make a new RSVP event object
    new_rsvp = RsvpEvent(userProfile=user_prof, event=event)
    if (rsvp_choice == 'J'):
        new_rsvp.rsvp_choice='J'
    elif (rsvp_choice == 'M'):
        new_rsvp.rsvp_choice='M'
    else:
        new_rsvp.rsvp_choice='D'
    
    # TODO error if RSVP choices aren't what is expected
    new_rsvp.save()
    return json_response({
      'success': True
    })

@login_required
def get_event_rsvp_user(request, event_id):
    context = {}
    event_get = get_object_or_404(Event, id=event_id)
    user_prof = get_object_or_404(UserProfile, user=request.user)

    rsvp = get_object_or_404(RsvpEvent, event=event_get, userProfile=user_prof)
    print rsvp.get_rsvp_choice_display()
    context['rsvp'] = rsvp
    context['user'] = user_prof
    
    return render(request, 'user.xml', context, content_type='application/xml')

def get_user(request, username):
    context = {}
    user = get_object_or_404(User, username=username)
    user_prof = get_object_or_404(UserProfile, user=user)

    rsvps = RsvpEvent.objects.filter(userProfile = user_prof)
    
    context['user'] = user_prof
    context['rsvps'] = rsvps

    return render(request, 'user.xml', context, content_type='application/xml')

# Gets a list of users and sorts them by username
def get_userlist(request):
    context = {'users':User.objects.all().order_by('username')}

    # Also keeps tracks of followers to keep buttons highlighted
    if request.user.is_authenticated():
	user_prof = UserProfile.objects.get(user=request.user)
	fol_users = user_prof.fol_users
	list_fol = fol_users.split(",")
	context['followusers'] = list_fol[1:]
    return render(request, 'userlist.xml', context, content_type='application/xml');

# Gets a list of the events by the date started.
# When creating the eventlist.xml, do some checking to see if the event is already over,
# ongoing currently, or something in the future so it's easier to parse in the future
def get_eventlist(request):
    context = {}
    events = Event.objects.order_by('-datetime_start')
    context['events'] = events
    print events
    return render(request, 'eventlist.xml', context, content_type='application/xml');

#    return json_response({
#        'events' : serializers.serialize('json', events)
#    })

# Returns own user's events only
@login_required
def get_user_eventlist(request):
    context = {}
    context['events'] = Event.objects.filter(user = request.user)
    return render(request, 'eventlist.xml', context, content_type='application/xml');

def get_photo(request, id):
    # Parses URL to get user info
    urlencode = request.GET.urlencode()

    event = get_object_or_404(Event, id=id)
    if not event.picture:
	raise Http404

    content_type = guess_type(event.picture.name)
    return HttpResponse(event.picture, mimetype=content_type)

# Attempt to login.  If successful, redirects to main page, otherwise displays
# login html page with error.
def login_attempt(request):
    context = {}
    errors = []

    # Just display the registration form if this is a GET request
    if request.method == 'GET' :
        return render(request, 'login.html', context)

    # Attempts to log in.  Logs in if user is active
    uname = request.POST['username']
    pword = request.POST['password']
    user = authenticate(username=uname, password=pword)
    if user is not None:
        if user.is_active:
            login(request, user)
            return json_response({
                    'success': True,
                    'username' : user.username,
                })
        else:
            errors.append('Not confirmed yet')
    else:
        errors.append('User not real')
    
    context['errors'] = errors

    #return render(request, 'login.html', context)
    return json_response({
            'success': False,
            'errors': errors,
        })

def logout_view(request):
    logout(request)
    return redirect('home')

# For confirmation code
def confirm(request):
    context = {}
    errors = []
    
    # Parses URL and sees if it matches any of the confirmation strings
    urlencode = request.GET.urlencode()
    urlencode = urlencode[:-1]
    if len(UserProfile.objects.filter(conf_str = urlencode)) > 0:
        users =  UserProfile.objects.filter(conf_str = urlencode)
        user = list(users[:1])
        
        # In the case that it's already been confirmed
        if (user[0].user.is_active != False):
            errors.append("Already confirmed!")
            context['errors'] = errors
            return render(request, 'confirmation.html', context)

        # Otherwise make user active adn therefore confirmed
        user[0].user.is_active = True
        user[0].user.save()
        user[0].save()
        return render(request, 'confirmation.html', context)
    else:
        errors.append('Not a valid confirmation code')
    
    context['errors'] = errors

    return render(request, 'confirmation.html', context) 

# Registration of a user
def register(request):
    context = {}

    # Just display the registration form if this is a GET request
    if request.method == 'GET' :
        context['form'] = RegistrationForm()
        return render(request, 'register.html', context)

    form = RegistrationForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return json_response({
            'success': False,
            'errors': dict(form.errors.items()),
        })

    # Creates a random confirmation string 32 characters long
    confirmation_str = ''.join([random.choice(string.ascii_letters \
				+ string.digits) for n in xrange(32)])

    # Sends email to given email.  Probably will be in spam inbox
    send_mail('Welcome to Georiot!', \
              "Welcome to Georiot.  This is a site that will allow you to not only manage your own events, but view other people's events as well.  Now that you've created an account, you need to confirm your account by clicking the following link.\n\n http://127.0.0.1:8000/blog/confirm/?"+confirmation_str, \
              'do.not.reply@georiot.com',\
               [request.POST['email']])

    # Creates the new user from valid form data
    new_user = User.objects.create_user(username=request.POST['username'],\
                                        password=request.POST['password1'],\
				        email=request.POST['email'])
    new_user.is_active = False
    new_user.save()
    new_userProf = UserProfile(user=new_user,\
                               conf_str=confirmation_str,\
                               street=request.POST['street'],\
                               city=request.POST['city'],\
                               state=request.POST['state'],\
                               zipcode=request.POST['zipcode'])
    new_userProf.save()

    return json_response({
        'success': True
    })
