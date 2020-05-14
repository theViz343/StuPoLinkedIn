from django.shortcuts import render, redirect
from django.middleware.csrf import get_token
import requests
from .models import User, ProfileURLForm, UserForm
import json
import os
import string
import random
from django.http import HttpResponse
# Create your views here.
state=""

def index(request):
    users=User.objects.all()
    context={
        'users': users,
    }
    return render(request,'LinkedInAuth/index.html',context=context)

def authorize(request):
    dir_name = os.path.dirname( __file__ )
    path = os.path.join( dir_name, '../../config.json' )
    f = open( path )
    private_data = json.load( f )
    client_id = private_data['client_id']
    client_secret = private_data['client_secret']
    redirect_uri = 'http://127.0.0.1:8000/auth/linkedin'
    auth_base_url = 'https://www.linkedin.com/oauth/v2/authorization'
    global state
    state=str(get_token(request))
    parameters = {
        'response_type' : 'code',
        'client_id' : client_id,
        'redirect_uri' : redirect_uri,
        'scope' : 'r_liteprofile r_emailaddress',
        'state' : state,

    }
    auth_initial=requests.get(auth_base_url,parameters)
    if str(auth_initial.status_code) == '200':
        user_auth_link=auth_initial.url
    return redirect(user_auth_link)

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

def auth_redirect(request):
    dir_name = os.path.dirname( __file__ )
    path = os.path.join( dir_name, '../../config.json' )
    f = open( path )
    private_data = json.load( f )
    client_id = private_data['client_id']
    client_secret = private_data['client_secret']
    redirect_uri = 'http://127.0.0.1:8000/auth/linkedin'
    if request.GET:
        code=request.GET.get('code','')
        returned_state=str(request.GET.get('state',''))
        global state
        if state==returned_state:
            params={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri,
                'client_id': client_id,
                'client_secret': client_secret,
                'Content-Type': 'x-www-form-urlencoded',
            }

            auth_second=requests.post('https://www.linkedin.com/oauth/v2/accessToken',params)
            access_token = auth_second.json()['access_token']

            # API Authorization Done.
            # ------------------------------------------------------------------------------------------------------------------
            # API Lookups

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
            #user.save_image_from_url()
            #user.save()
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
    elif request.POST:
        id = request.POST.get( 'id' )
        user = User.objects.get( id=id )
        profile_form = ProfileURLForm( request.POST, instance=user )
        if profile_form.is_valid() :
            profile_form.save()
            user.correct_profile_url()
            user.save()
            return redirect( 'index' )