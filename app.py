from bottle import route, run, template, static_file, request, redirect, default_app
from collections import Counter
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import json
import httplib2
from beaker.middleware import SessionMiddleware
from db import init_db, log_search, get_recent_searches


################################################################### GLOBAL VARIABLES
global_keyword_dict = Counter() # keeps track of keywords and their occurances among all users

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}

init_db() # initialize database

################################################################## ROUTING
# Home page
@route('/')
def home():
    session = request.environ.get('beaker.session')

    # check if user is logged in
    if 'user_email' in session: # signed-in mode
        user_email = session['user_email']
        recent = get_recent_searches(user_email)
        return template('index', keyword_dict={}, top_20=global_keyword_dict.most_common(20), logged_in=True, user_email=user_email, recent=recent)
    else: # anonymous mode
        return template('index', keyword_dict={}, top_20=global_keyword_dict.most_common(20), logged_in=False, user_email=None, recent=[])


# Loading style.css and other static files
@route('/static/<filepath:path>')
def server_static(filepath):
    """Serving static files """
    return static_file(filepath, root='./static')


# Google login
@route('/signin', method="GET")
def signin():
    # generate Google login URL and redirect to it
    flow = flow_from_clientsecrets("client_secret.json",
        scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
        redirect_uri='http://localhost:8080/redirect')
    uri = flow.step1_get_authorize_url()
    redirect(str(uri))


# Redirect to GoFetch main page
@route('/redirect')
def redirect_page():
    session = request.environ.get('beaker.session')
    
    code = request.query.get("code", "")
    scope = ['profile', 'email']

    with open('client_secret.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    ID = data['web']['client_id']
    SECRET = data['web']['client_secret']
    
    flow = OAuth2WebServerFlow(ID, SECRET, scope=scope,
    redirect_uri="http://localhost:8080/redirect")
    credentials = flow.step2_exchange(code)
    http = httplib2.Http()
    http = credentials.authorize(http)
    users_service = build('oauth2', 'v2', http=http)
    user_document = users_service.userinfo().get().execute()
    user_email = user_document['email']

    # save email in session
    session['user_email'] = user_email
    session.save()
    redirect('/')


# Handle input form submission 
@route('/search', method="GET")
def formHandler():
    session = request.environ.get('beaker.session')
    keywords = request.query.get('keywords') # input from user
    keyword_dict = Counter() # keeping track of word occurance
    recent = [] # 10 recent searches

    if keywords: # if user entered a keyword
        keyword_list = keywords.split()
        keyword_dict.update(keyword_list)
        global_keyword_dict.update(keyword_list)

        if 'user_email' in session: # signed-in mode
            user_email = session['user_email']

            for kw in keyword_list:
                log_search(user_email, kw) # add word to database
            recent = get_recent_searches(user_email) # get recent words from database
            response = template('index', keyword_dict=keyword_dict, top_20=global_keyword_dict.most_common(20),
                                logged_in=True, user_email=user_email, recent=recent)
        else: # anonymous mode
            response = template('index', keyword_dict=keyword_dict, top_20=global_keyword_dict.most_common(20),
                                logged_in=False, user_email=None, recent=[])

    # clear the URL to prevent resubmission
    response += '<script>if(window.history.replaceState){window.history.replaceState(null,null,"/");}</script>'
    return response


# Log out
@route('/logout')
def logout():
    # clear user's session data
    session = request.environ.get('beaker.session')
    session.clear() 
    redirect('/') # redirect to main page


app = SessionMiddleware(default_app(), session_opts)
run(app=app, host='0.0.0.0', port=8080, debug=True, reloader=True)