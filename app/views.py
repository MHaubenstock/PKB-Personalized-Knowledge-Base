from app import app, db, login_manager
from flask import render_template, flash, redirect, session, url_for, request, g
from app.models import User
from app.models import UserTopic
from app.forms import LoginForm, RegisterForm, EditTopic
from flask.ext.login import login_user, logout_user, current_user, login_required
import os

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# sets current user from flask-login to g.user
@app.before_request
def before_request():
    g.user = current_user

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/')
@app.route('/home', methods = ['GET', 'POST'])
@login_required
def home():
    #Get top level topic titles
    user = g.user
    topLevelTopicTitles = [t.title for t in user.topics]
    return render_template('home.html', topics=topLevelTopicTitles)


# this is the default page that shows up when connecting
# to the website (or localhost)
@app.route('/login', methods = ['GET', 'POST'])
def login():
    # if user is logged in, redirect them to home
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('home'))
    form = LoginForm()
    # tries to login user
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        session['remember_me'] = form.remember_me.data
        registered_user = User.query.filter_by(username=username).first()
        if registered_user is not None:
            if registered_user.check_password(password):
                remember_me = False
                if 'remember_me' in session:
                    remember_me = session['remember_me']
                    session.pop('remember_me', None)
                login_user(registered_user, remember = remember_me)
                flash('Logged in successfully')
                return redirect(request.args.get('next') or url_for('home'))
            else:
                form.password.errors.append("Invalid password!")
        else:
            form.username.errors.append("Invalid username!")
    return render_template('login.html', title = 'Sign In', form = form)

@app.route('/register' , methods=['GET','POST'])
def register():
    # if user is logged in, redirect them to home
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('home'))
    form = RegisterForm()
    # tries to register user
    if form.validate_on_submit():
        new_user = User.query.filter_by(username=form.username.data).first()
        if new_user is None:
            user = User(form.username.data, form.password.data)
            db.session.add(user)
            db.session.commit()

            flash('User successfully registered')
            return redirect(url_for('login'))
        else:
            form.username.errors.append('That username is already taken!')
    return render_template('register.html', form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/<topicParent>/<topic>', methods = ['GET', 'POST'])
@login_required
# you don't need to pass in None as default arguments, since users
# won't be able to click on topics that don't exist. Can replace with:
#
# def topic(topic, topicParent):
def topic(topic = None, topicParent = None):
    '''
    db.session.add(UserTopic("Test Topic", g.user.username, ["test", "nlah"]))
    db.session.add(UserTopic("Test Topic2", "Test Topic", ["test2", "nlah2"]))
    db.session.add(UserTopic("Test Topic3", "Test Topic", ["test3", "nlah3"]))
    '''
    # May be better to use:
    # thisTopic = UserTopic.query.filter(title=topic).first()
    # - the "title" is a keyword argument, not a boolean
    thisTopic = UserTopic.query.filter(UserTopic.title == topic).first()
    
    # this can be replaced with:
    # if thisTopic:
    if not thisTopic is None:
        description = thisTopic.description
        tags = thisTopic.tags
    # why would they be able to click on a topic that doesn't exist?
    else: #Did not find topic, don't go to page
        return redirect(url_for('home'))

    # May be better to use:
    # thisTopic = UserTopic.query.filter(parent = topic).first().all()
    # - the "title" is a keyword argument, not a boolean
    subTopics = [s.title for s in UserTopic.query.filter(UserTopic.parent == topic).all()]

    return render_template('topic.html', topic = topic, subTopics = subTopics, description = description, tags = tags)

# let's make a pretty usl like this!
@app.route('/create_new_topic')
@app.route('/<topicParent>/<topic>/edit_topic', methods = ['GET', 'POST'])
@login_required
def edittopic(topic = None, topicParent = None, tags = None):
    """
    # Why is this here??

    topic = request.args.get('topic')
    topicParent = request.args.get('topicParent')
    tags = request.args.getlist('tags')
    """

    if tags:
        tags = ' '.join(tags)
    else:
        tags = ''

    # this doesn't do what you think it does, we need to query the DB for 
    # the topic's description, passed in by button click
    description = request.args.get('description')
    # need this:
    if topic:
        description = UserTopic.query.filter(title=topic)
    else:
        topic = ''
    #For submitting topic data
    form = EditTopic()
    #if form.validate_on_submit():

    return render_template('edittopic.html', topic = topic, topicParent = topicParent, tags = tags, form = form)

