from django.db import models
from django import forms
import string
import random
import requests
import tempfile
import os
import io
from PIL import Image
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File


# Create your models here.
def content_file_name(self, filename) :
    return '/'.join( ['users', self.first_name + "_" + self.last_name, filename] )


class User( models.Model ) :
    id = models.AutoField(primary_key=True)
    first_name = models.CharField( verbose_name='FirstName', max_length=30 )
    last_name = models.CharField( verbose_name='LastName', max_length=30 )

    def __str__(self) :
        return self.first_name + " " + self.last_name

class LinkedInDetails( models.Model ) :
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    linkedin_id = models.CharField( verbose_name='LinkedIn Id', primary_key=True, max_length=20, default='initial' )
    image_url = models.CharField( verbose_name='Profile Picture URL', max_length=200 )
    profile_url = models.CharField( verbose_name='LinkedIn Profile URL', default='', max_length=100 )

    def __str__(self):
        return str(self.user) + "'s details"

    def correct_profile_url(self) :
        if not (self.profile_url.startswith( "https://" ) or self.profile_url.startswith( "http://" )) :
            self.profile_url = "https://" + self.profile_url




class UserForm( forms.ModelForm ) :
    class Meta :
        model = User
        fields = ['first_name', 'last_name']
        widgets = {

            'first_name' : forms.TextInput(
                attrs={
                    'class' : 'form-control',
                    'name' : "First Name",
                    'placeholder' : "First Name",
                    'style' : "font-family: ABeeZee, sans-serif;",

                }
            ),
            'last_name' : forms.TextInput(
                attrs={
                    'class' : 'form-control',
                    'name' : "Last Name",
                    'placeholder' : "Last Name",
                    'style' : "font-family: ABeeZee, sans-serif;",

                }
            ),

        }


class ProfileURLForm( forms.ModelForm ) :
    class Meta :
        model = LinkedInDetails
        fields = ['profile_url']
        widgets = {

            'profile_url' : forms.TextInput(
                attrs={
                    'class' : 'form-control',
                    'name' : "Profile URL",
                    'placeholder' : "Your LinkedIn Profile URL",
                    'required pattern' : "www.linkedin.com/in/.*",
                    'style' : "font-family: ABeeZee, sans-serif;",

                }
            ),
        }
