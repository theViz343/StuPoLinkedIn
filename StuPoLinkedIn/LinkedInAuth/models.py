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
class User(models.Model):
    id =models.CharField(verbose_name='LinkedIn Id',primary_key=True,max_length=20,default='initial')
    first_name = models.CharField(verbose_name='FirstName', max_length=30)
    last_name = models.CharField(verbose_name='LastName', max_length=30)
    profile_pic_url = models.CharField( verbose_name='Profile Picture URL', null=True, max_length=200)
    profile_pic = models.ImageField(verbose_name='Profile Picture',upload_to=content_file_name,null=True,help_text='Please upload image of size 100X100 px only',blank=True)
    email = models.EmailField( verbose_name='Email Address',default='')
    profile_url = models.CharField( verbose_name='LinkedIn Profile URL',default='',max_length=100)

    def __str__(self):
        return self.first_name+" "+self.last_name


    def save_image_from_url(self) :
        """
        Save remote images from url to image field.
        Requires python-requests
        """
        r = requests.get( self.profile_pic_url )

        if r.status_code == 200 :
            f = io.BytesIO( r.content )
            print( f )
            img = Image.open( f )
            #img.save('')
            self.profile_pic.save(self.first_name+"_"+self.last_name+".jpeg", img)


    def getImage(self) :
        url = self.profile_pic_url
        image_object = requests.get( url, stream=True )

        # Was the request OK?
        if image_object.status_code != requests.codes.ok :
            # Nope, error handling, skip file etc etc etc
            return False

        # Get the filename from the url, used for saving later
        file_name = self.first_name + " " + self.last_name

        # Create a temporary file
        im = tempfile.NamedTemporaryFile()

        # Read the streamed image in sections
        for block in image_object.iter_content( 1024 * 8 ) :

            # If no more file then stop
            if not block :
                break

            # Write image block to temporary file
            im.write( block )
        #self.profile_pic.save(file_name,files.File(im))
        return True

    def correct_profile_url(self):
        if not (self.profile_url.startswith("https://") or self.profile_url.startswith("http://")):
            self.profile_url = "https://" + self.profile_url



class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields= ['first_name','last_name','email','profile_url','profile_pic']
        widgets={

            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'name': "First Name",
                    'placeholder': "First Name",
                    'style': "font-family: ABeeZee, sans-serif;",

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
            'email' : forms.EmailInput(
                attrs={
                    'class' : 'form-control',
                    'name' : "Email",
                    'placeholder' : "Email Address",
                    'style' : "font-family: ABeeZee, sans-serif;",

                }
            ),
            'profile_url' : forms.TextInput(
                attrs={
                    'class' : 'form-control',
                    'name' : "Profile URL",
                    'placeholder' : "Your LinkedIn Profile URL",
                    'required pattern': "www.linkedin.com/in/.*",
                    'style' : "font-family: ABeeZee, sans-serif;",

                }
            ),
            'profile_pic': forms.FileInput(
                attrs={
                    'name': "Profile Picture",
                    'accept': "image/*",
                    'required': True,
                    'style': "font-family: ABeeZee, sans-serif;",
                }
            )
        }

class ProfileURLForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_url']
        widgets= {

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