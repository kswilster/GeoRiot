from django import forms

from django.contrib.auth.models import User
from models import *
from django.forms import SplitDateTimeWidget, Textarea
from django.contrib.admin import widgets
from datetimewidget.widgets import DateTimeWidget
from localflavor.us.us_states import STATE_CHOICES
from localflavor.us.forms import USStateSelect
from localflavor.us.forms import USStateField

import datetime
from datetime import date, time, datetime
from django.utils import timezone

calendar_widget = forms.widgets.DateInput(attrs={'class': 'date-pick'}, format='%m/%d/%Y')
time_widget = forms.widgets.TimeInput(attrs={'class': 'time-pick'})
valid_time_formats = ['%H:%M', '%I:%M%p', '%I:%M %p']

dateTimeOptions = {
'format': 'mm/dd/yyyy HH:ii P',
'autoclose': 'true',
'showMeridian' : 'true'
}

class EventForm(forms.ModelForm):
    class Meta:
        model = Event

        widgets = {'picture' : forms.FileInput(),\
                   'datetime_start' : DateTimeWidget(options = dateTimeOptions),\
                   'datetime_end' : DateTimeWidget(options = dateTimeOptions),\
                   'state' : USStateSelect()}
        
	fields = ('title', 'description', 'picture', 'datetime_start', 'datetime_end', 'street', 'city', 'state', 'zipcode')

    def clean(self):
        cleaned_data = super(EventForm, self).clean()
        error_messages = []

        # Make sure that the event starting and ending times don't conflict
        datetime_today = timezone.now()
        datetime_start = cleaned_data.get('datetime_start')
        datetime_end = cleaned_data.get('datetime_end')
        if (datetime_start != None and datetime_end != None):
            if (datetime_start >= datetime_end):
                error_messages.append("Event cannot start after the end date")
            if (datetime_today > datetime_start):
                error_messages.append("The starting time must be after the current time and date")
        
        if len(error_messages):
            raise forms.ValidationError(' & '.join(error_messages))
        return cleaned_data
          

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length = 20)
    password1 = forms.CharField(max_length = 200, 
                                label='Password', 
                                widget = forms.PasswordInput())
    password2 = forms.CharField(max_length = 200,
                                label='Confirm password',
                                widget = forms.PasswordInput())
    email = forms.CharField(max_length = 200)
    street = forms.CharField(max_length = 500)
    city = forms.CharField(max_length = 500)
    state = USStateField(widget=USStateSelect())
    zipcode = forms.CharField(max_length = 500)


    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(RegistrationForm, self).clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username
