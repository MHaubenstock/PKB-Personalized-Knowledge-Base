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

@app.route('/home/<username>', methods = ['GET', 'POST'])
@login_required
def home(username):
    user = g.user
    #Get top level topic titles
    topLevelTopicTitles = [t for t in user.topics]
    return render_template('home.html', username=user.username, topics=topLevelTopicTitles)


# this is the default page that shows up when connecting
# to the website (or localhost)
@app.route('/', methods = ['GET', 'POST'])
@app.route('/login', methods = ['GET', 'POST'])
def login():
    # if user is logged in, redirect them to home
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('home', username=g.user.username))
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
                return redirect(request.args.get('next') or url_for('home', username=registered_user.username))
            else:
                form.password.errors.append("Invalid password!")
        else:
            form.username.errors.append("Invalid username!")
    return render_template('login.html', title = 'Sign In', form = form)

@app.route('/register' , methods=['GET','POST'])
def register():
    # if user is logged in, redirect them to home
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('home', username=g.user.username))
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
    return redirect(url_for('login'))

@app.route('/<topicParent>/<topic_name>', methods = ['GET', 'POST'])
@login_required
def topic(topic_name, topicParent):
    topic = UserTopic.query.filter(UserTopic.title == topic_name).first()
    
    if topic is None:
        return redirect(url_for('home', username=g.user.username))

    description = topic.description
    tags = topic.tags
    subTopics = [s.title for s in UserTopic.query.filter(UserTopic.parent == topic_name).all()]
    topicParentParent = UserTopic.query.filter(UserTopic.title == topic_name).first().parent

    return render_template('topic.html', topic = topic, topicParent = topicParent, topicParentParent = topicParentParent, subTopics = subTopics, description = description, tags = tags)

@app.route('/<user>/create_new_topic', methods = ['GET', 'POST'])
@app.route('/<topicParent>/<topic>/edit_topic', methods = ['GET', 'POST'])
@login_required
def edittopic(user=None,topic_name=None,topicParent=None):
    #For submitting topic data
    form = EditTopic()
    topic = UserTopic.query.filter(UserTopic.title == topic_name).first()
    
    if topic:
        if theTopic.tags:
            tags = ', '.join(topic.tags)
        else:
            tags = ''
    
        description = topic.description
    else:
        topic = ''
        tags = ''
        description = ''

        # not passing topicparent to the function when it's not part of the route for 
        # some reason, so need to get it manually
        topicParent = request.args.get('topicParent')

    #couldn't get if form.validate_on_submit(): working
    if request.method == 'POST': #and form.validate():
        #if it's a new topic
        if topic is None:
            topic = UserTopic(form.topicTitle.data, topicParent, [])
            db.session.add(topic)

        #Save topic information to the topic
        topic.title = form.topicTitle.data
        topic.tags = list(filter(lambda x: not x == '', form.tags.data.replace(' ', '').split(',')))
        topic.description = form.description.data
        topic.parent = topicParent

        #if it's a top level topic, add it to user topics
        if topic.parent == g.user.username:
            g.user.topics.append(topic)
        
        db.session.commit()

        return redirect(url_for('topic', topic=theTopic.title, topicParent=theTopic.parent))

    return render_template('edittopic.html', topic = topic, topicParent = topicParent, tags = tags, form = form)

