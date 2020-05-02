from django.shortcuts import render
import requests
from .models import User
import json
import os


# Create your views here.
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
    parameters = {
        'response_type' : 'code',
        'client_id' : client_id,
        'redirect_uri' : redirect_uri,
        'scope' : 'r_liteprofile',

    }
    auth_initial=requests.get(auth_base_url,parameters)
    if str(auth_initial.status_code) == '200':
        user_auth_link=auth_initial.url
    return render(request,'LinkedInAuth/authorize.html',{'link': user_auth_link,})

def auth_redirect(request):
    dir_name = os.path.dirname( __file__ )
    path = os.path.join( dir_name, '../../config.json' )
    f = open( path )
    private_data = json.load( f )
    client_id = private_data['client_id']
    client_secret = private_data['client_secret']
    redirect_uri = 'http://127.0.0.1:8000/auth/linkedin'

    code=request.GET.get('code','')
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
    params2 = {
        'oauth2_access_token': access_token,
        'projection': '(id,firstName,lastName,headline,vanityName,profilePicture(displayImage~:playableStreams))'
    }
    content=requests.get('https://api.linkedin.com/v2/me',params2)

    content_json=content.json()
    first_name = content_json['firstName']['localized']['en_US']
    last_name = content_json['lastName']['localized']['en_US']
    profile_pic_url=content_json['profilePicture']['displayImage~']['elements'][0]['identifiers'][0]['identifier']
    id=content_json['id']

    user= User(first_name=first_name,last_name=last_name,profile_pic_url=profile_pic_url,id=id)
    user.save()
    return render(request,'LinkedInAuth/redirect.html',{'name': first_name+" "+last_name,
                                                        'profile_pic_url': profile_pic_url,
                                                        })