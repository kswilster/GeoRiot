from django.db import models
import datetime
from localflavor.us.us_states import STATE_CHOICES
from localflavor.us.models import USStateField

# User class for built-in authenitcation module
from django.contrib.auth.models import User

class Event(models.Model):
    user = models.ForeignKey(User)

    title = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    picture = models.ImageField(upload_to='blog-photos', blank=True)

    # date, time and location of when the event will take place
    datetime_start = models.DateTimeField()
    datetime_end = models.DateTimeField()
    street = models.CharField(max_length=500)
    city = models.CharField(max_length=500)
    state = USStateField()
    zipcode = models.CharField(max_length=10)

    def __unicode__(self):
        return self.description

    @staticmethod
    def get_posts(user):
	return Event.objects.filter(user=user)

    @staticmethod
    def get_posts_ul(userlist):
	userthing = Event.objects.none()

        for user_fl in userlist:
             userthing = userthing |\
                         Event.objects.filter(user=user_fl).order_by('-datetime_start')

	return userthing

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    fol_users = models.TextField()
    conf_str = models.CharField(max_length=32)
    street = models.CharField(max_length=500)
    city = models.CharField(max_length=500)
    state = USStateField()
    zipcode = models.CharField(max_length=10)

# A model to manage users and the events that they have RSVPed
class RsvpEvent(models.Model):
    RSVP_CHOICES = (
        ('J', 'Join'),
        ('M', 'Maybe'),
        ('D', 'Decline'),
    )
    userProfile = models.ForeignKey(UserProfile)
    event = models.ForeignKey(Event)
    rsvp_choice = models.CharField(max_length=1, choices=RSVP_CHOICES)
    

