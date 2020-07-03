import requests

def app_auth(data,csrf_token):
    client_id = data['client_id']
    client_secret = data['client_secret']
    redirect_uri = data['redirect_uri']
    base_url = 'https://www.linkedin.com/oauth/v2/authorization'
    state = csrf_token
    parameters = {
        'response_type' : 'code',
        'client_id' : client_id,
        'redirect_uri' : redirect_uri,
        'scope' : 'r_liteprofile r_emailaddress',
        'state' : state,

    }
    auth = requests.get( base_url, parameters )
    if str( auth.status_code ) == '200' :
        user_auth_link = auth.url
        return user_auth_link
    else:
        return "error"

def user_auth(data,request,csrf_token):
    client_id = data['client_id']
    client_secret = data['client_secret']
    redirect_uri = data['redirect_uri']
    auth_info = {
        'auth': False,
        'access_token' : "",
    }
    if request.GET:
        auth_info['auth'] = True
        code=request.GET.get('code','')
        returned_state=str(request.GET.get('state',''))
        if csrf_token==returned_state:
            params={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri,
                'client_id': client_id,
                'client_secret': client_secret,
                'Content-Type': 'x-www-form-urlencoded',
            }

            auth = requests.post('https://www.linkedin.com/oauth/v2/accessToken',params)
            if str(auth.status_code) == '200':
                access_token = auth.json()['access_token']
                auth_info['access_token']=access_token
                auth_info['success']=True
                return auth_info
            else:
                auth_info['success']=False
                return auth_info
    else:

        return auth_info
