from django.shortcuts import render, redirect
from django.middleware.csrf import get_token
import requests
from .models import User, ProfileURLForm, UserForm
import json
import os
import string
import random
from django.http import HttpResponse
from .auth import app_auth, user_auth
# Create your views here.
state=""

def index(request):
    users=User.objects.all()
    context={
        'users': users,
    }
    return render(request,'LinkedInAuth/index.html',context=context)

def register(request):
    if request.POST:
        random_id = ''.join( random.choices( string.ascii_uppercase + string.ascii_lowercase + string.digits, k=10 ) )
        form = UserForm(request.POST, request.FILES)
        form.save()
        user=User.objects.get(id='initial')

        user.profile_pic_url=user.profile_pic.url
        user.correct_profile_url()
        user.delete()
        user.id=random_id
        user.save()
        return redirect('index')
    else:
        form = UserForm()
        return render( request, 'LinkedInAuth/register.html', context={
            'form' : form,
        })

def authorize(request):
    dir_name = os.path.dirname( __file__ )
    path = os.path.join( dir_name, '../../config.json' )
    f = open( path )
    data = json.load( f )
    data['redirect_uri'] = 'http://127.0.0.1:8000/auth/linkedin'
    global state
    state = str(get_token(request))
    user_auth_link = app_auth(data,state)
    return redirect(user_auth_link)

def auth_redirect(request):
    dir_name = os.path.dirname( __file__ )
    path = os.path.join( dir_name, '../../config.json' )
    f = open( path )
    data = json.load( f )
    data['redirect_uri'] = 'http://127.0.0.1:8000/auth/linkedin'
    auth_info = user_auth(data,request,state)

    if auth_info['auth']==True: # If it is an authorization call

        if auth_info['success']==True:
            access_token=auth_info['access_token']

            #    Id,Name and Profile Pic Lookup
            params = {
                'oauth2_access_token': access_token,
                'projection': '(id,firstName,lastName,headline,vanityName,profilePicture(displayImage~:playableStreams))'
            }
            content=requests.get('https://api.linkedin.com/v2/me',params)

            content_json=content.json()
            first_name = content_json['firstName']['localized']['en_US']
            last_name = content_json['lastName']['localized']['en_US']
            profile_pic_url=content_json['profilePicture']['displayImage~']['elements'][0]['identifiers'][0]['identifier']
            id=content_json['id']

            #    Email Address Lookup
            params = {
                'oauth2_access_token' : access_token,
                'q' : 'members',
                'projection' : '(elements*(primary,type,handle~))'
            }
            content = requests.get( 'https://api.linkedin.com/v2/clientAwareMemberHandles', params )

            content_json = content.json()
            email_address=content_json['elements'][0]['handle~']['emailAddress']

            user= User(first_name=first_name,last_name=last_name,profile_pic_url=profile_pic_url,id=id,email=email_address)
            user.save()

            form = ProfileURLForm
            return render( request, 'LinkedInAuth/redirect.html', {'name' : first_name + " " + last_name,
                                                                   'profile_pic_url' : profile_pic_url,
                                                                   'email' : email_address,
                                                                   'content' : content.text,
                                                                   'id' : id,
                                                                   'form' : form
                                                                   } )
        else:
                return HttpResponse('There was an error')

    elif auth_info['auth']==False: # If it is the profile url form call

        id = request.POST.get( 'id' )
        user = User.objects.get( id=id )
        profile_form = ProfileURLForm( request.POST, instance=user )
        if profile_form.is_valid() :
            profile_form.save()
            user.correct_profile_url()
            user.save()
            return redirect( 'index' )