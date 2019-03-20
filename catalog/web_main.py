from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from webdb_setup import Base, WebsiteName, ToolName, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

engine = create_engine('sqlite:///websites.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Website"

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create anti-forgery state token
nfs_gmb = session.query(WebsiteName).all()


# login
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    nfs_gmb = session.query(WebsiteName).all()
    nafs = session.query(ToolName).all()
    return render_template('login.html',
                           STATE=state, nfs_gmb=nfs_gmb, nafs=nafs)
    # return render_template('myhome.html', STATE=state
    # nfs_gmb=nfs_gmb,nafs=nafs)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# User Helper Functions
def createUser(login_session):
    User1 = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(User1)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session

#####
# Home


@app.route('/')
@app.route('/home')
def home():
    nfs_gmb = session.query(WebsiteName).all()
    return render_template('myhome.html', nfs_gmb=nfs_gmb)

#####
# Website hub for admins


@app.route('/WebsiteHub')
def WebsiteHub():
    try:
        if login_session['username']:
            name = login_session['username']
            nfs_gmb = session.query(WebsiteName).all()
            nfs = session.query(WebsiteName).all()
            nafs = session.query(ToolName).all()
            return render_template('myhome.html', nfs_gmb=nfs_gmb,
                                   nfs=nfs, nafs=nafs, uname=name)
    except:
        return redirect(url_for('showLogin'))

######
# Showing items


@app.route('/WebsiteHub/<int:naid>/AllWebsite')
def showWebsite(naid):
    nfs_gmb = session.query(WebsiteName).all()
    nfs = session.query(WebsiteName).filter_by(id=naid).one()
    nafs = session.query(ToolName).filter_by(websitenameid=naid).all()
    try:
        if login_session['username']:
            return render_template('showWebsite.html', nfs_gmb=nfs_gmb,
                                   nfs=nfs, nafs=nafs,
                                   uname=login_session['username'])
    except:
        return render_template('showWebsite.html',
                               nfs_gmb=nfs_gmb, nfs=nfs, nafs=nafs)

#####
# Add New Tool


@app.route('/WebsiteHub/addWebsiteName', methods=['POST', 'GET'])
def addWebsiteName():
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
        websitename = WebsiteName(name=request.form['name'],
                                  user_id=login_session['user_id'])
        session.add(websitename)
        session.commit()
        return redirect(url_for('WebsiteHub'))
    else:
        return render_template('addWebsiteName.html', nfs_gmb=nfs_gmb)

########
# Edit Website name


@app.route('/WebsiteHub/<int:naid>/edit', methods=['POST', 'GET'])
def editWebsiteName(naid):
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    editWebsiteName = session.query(WebsiteName).filter_by(id=naid).one()
    creator = getUserInfo(editWebsiteName.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this WebsiteName."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('WebsiteHub'))
    if request.method == "POST":
        if request.form['name']:
            editWebsiteName.name = request.form['name']
        session.add(editWebsiteName)
        session.commit()
        flash("editWebsiteName Edited Successfully")
        return redirect(url_for('WebsiteHub'))
    else:
        # nfs_gmb is global variable we can them in entire application
        return render_template('editWebsiteName.html',
                               na=editWebsiteName, nfs_gmb=nfs_gmb)

######
# Delete WebsiteName


@app.route('/WebsiteHub/<int:naid>/delete', methods=['POST', 'GET'])
def deleteWebsiteName(naid):
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    na = session.query(WebsiteName).filter_by(id=naid).one()
    creator = getUserInfo(na.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot Delete this Website name."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('WebsiteHub'))
    if request.method == "POST":
        session.delete(na)
        session.commit()
        flash("WebsiteName Deleted Successfully")
        return redirect(url_for('WebsiteHub'))
    else:
        return render_template('deleteWebsiteName.html', na=na,
                               nfs_gmb=nfs_gmb)

######
# Add New Website Tool Details


@app.route('/WebsiteHub/addWebsiteName/'
           'addWebsiteToolDetails/<string:naname>/add',
           methods=['GET', 'POST'])
def addWebsiteToolDetails(naname):
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    nfs = session.query(WebsiteName).filter_by(name=naname).one()
    # See if the logged in user is not the owner of website
    creator = getUserInfo(nfs.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't add new Item edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showWebsite', naid=nfs.id))
    if request.method == 'POST':
        name = request.form['name']
        discription = request.form['discription']
        year = request.form['year']
        founder = request.form['founder']
        tooldetails = ToolName(name=name, discription=discription,
                               year=year,
                               founder=founder,
                               date=datetime.datetime.now(),
                               websitenameid=nfs.id,
                               user_id=login_session['user_id'])
        session.add(tooldetails)
        session.commit()
        return redirect(url_for('showWebsite', naid=nfs.id))
    else:
        return render_template('addWebsiteToolDetails.html',
                               naname=nfs.name, nfs_gmb=nfs_gmb)

######
# Edit Website Tool details


@app.route('/WebsiteHub/<int:naid>/<string:nftname>/edit',
           methods=['GET', 'POST'])
def editWebsiteTool(naid, nftname):
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    na = session.query(WebsiteName).filter_by(id=naid).one()
    tooldetails = session.query(ToolName).filter_by(name=nftname).one()
    # See if the logged in user is not the owner of website
    creator = getUserInfo(na.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't edit this Item edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showWebsite', naid=na.id))
    # POST methods
    if request.method == 'POST':
        tooldetails.name = request.form['name']
        tooldetails.discription = request.form['discription']
        tooldetails.year = request.form['year']
        tooldetails.founder = request.form['founder']
        tooldetails.date = datetime.datetime.now()
        session.add(tooldetails)
        session.commit()
        flash("Tool Edited Successfully")
        return redirect(url_for('showWebsite', naid=naid))
    else:
        return render_template('editWebsiteTool.html',
                               naid=naid, tooldetails=tooldetails,
                               nfs_gmb=nfs_gmb)

#####
# Delete Website tool


@app.route('/WebsiteHub/<int:naid>/<string:nftname>/delete',
           methods=['GET', 'POST'])
def deleteWebsiteTool(naid, nftname):
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    na = session.query(WebsiteName).filter_by(id=naid).one()
    tooldetails = session.query(ToolName).filter_by(name=nftname).one()
    # See if the logged in user is not the owner of website
    creator = getUserInfo(na.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't delete this book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showWebsite', naid=na.id))
    if request.method == "POST":
        session.delete(tooldetails)
        session.commit()
        flash("Deleted Website item Successfully")
        return redirect(url_for('showWebsite', naid=naid))
    else:
        return render_template('deleteWebsiteTool.html',
                               naid=naid, tooldetails=tooldetails,
                               nfs_gmb=nfs_gmb)

####
# Logout from current user


@app.route('/logout')
def logout():
    access_token = login_session['access_token']
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected....'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None,
                  headers={'content-type':
                           'application/x-www-form-urlencoded'})[0]
    print (result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps
                                 ('Successfully disconnected user..'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('showLogin'))
        # return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

#####
# Json


@app.route('/WebsiteHub/JSON')
def allWebsiteJSON():
    websitename = session.query(WebsiteName).all()
    category_dict = [c.serialize for c in websitename]
    for c in range(len(category_dict)):
        websitetoolname = [i.serialize for i in session.query(
                 ToolName).filter_by(
                 websitenameid=category_dict[c]["id"]).all()]
        if websitetoolname:
            category_dict[c]["website"] = websitetoolname
    return jsonify(WebsiteName=category_dict)

####


@app.route('/websiteHub/websiteName/JSON')
def categoriesJSON():
    website = session.query(WebsiteName).all()
    return jsonify(websiteName=[c.serialize for c in website])

####


@app.route('/WebsiteHub/website/JSON')
def toolJSON():
    tool = session.query(ToolName).all()
    return jsonify(website=[i.serialize for i in tool])

#####


@app.route('/WebsiteHub/<path:websitename>/website/JSON')
def categorytoolJSON(websitename):
    websiteName = session.query(WebsiteName).filter_by(name=websitename).one()
    website = session.query(ToolName).filter_by(websitename=websiteName).all()
    return jsonify(websiteName=[i.serialize for i in website])

#####


@app.route('/WebsiteHub/<path:websitename>/<path:websitetool_name>/JSON')
def ToolJSON(websitename, websitetool_name):
    websiteName = session.query(WebsiteName).filter_by(name=websitename).one()
    websiteToolName = session.query(ToolName).filter_by(
        name=websitetool_name, websitename=websiteName).one()
    return jsonify(websiteToolName=[websiteToolName.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=8000)
