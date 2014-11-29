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
            user = User(form.username.data, form.email.data, form.password.data)
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

@app.route('/home/<username>', methods = ['GET', 'POST'])
@login_required
def home(username):
    user = g.user
    #Get top level topic titles
    topLevelTopicTitles = [t for t in user.topics]
    return render_template('home.html', username=user.username, topics=topLevelTopicTitles)

@app.route('/<topic_parent>/<topic_name>', methods = ['GET', 'POST'])
@login_required
def topic(topic_name, topic_parent):
    topic = UserTopic.query.filter(UserTopic.title == topic_name).first()

    if topic is None:
        return redirect(url_for('home', username=g.user.username))

    description = topic.description
    tags = topic.tags
    subTopics = UserTopic.query.filter(UserTopic.parent == topic_name).all()
    topic_parent = UserTopic.query.filter_by(title=topic.parent).first()

    return render_template('topic.html', topic = topic, topic_parent=topic_parent, subTopics = subTopics, description = description, tags = tags)

@app.route('/<user>/<topic_parent>/<topic_name>/edit_topic', methods = ['GET', 'POST'])
@login_required
def edittopic(user,topic_name,topic_parent):
    #For submitting topic data
    form = EditTopic()

    topic = UserTopic.query.filter_by(title = topic_name).first()
    if topic is None:
        flash("That topic does not exist!")
        redirect(url_for('home', username=g.user.username))

    form.topicTitle.data = topic.title
    form.description.data = topic.description
    form.tags.data = ', '.join([str(tag) for tag in topic.tags])

    if form.validate_on_submit():
        # gets new form data to update topic with
        form = EditTopic(request.form)
        # saves topic information to the topic
        topic.title = form.topicTitle.data
        topic.tags = [x for x in form.tags.data.replace(' ', '').split(',') if x != ""]
        topic.description = form.description.data
        topic.parent = topic_parent

        db.session.merge(topic)
        db.session.commit()

        return redirect(url_for('topic', topic_name=topic.title, topic_parent=topic.parent))
    else:
        for error in form.errors:
            flash("Please enter a "+str(error)+" for "+topic_name)

    return render_template('edittopic.html', topic=topic, form=form)

@app.route('/<topic_parent>/create_new_topic', methods = ['GET', 'POST'])
@login_required
def create_new_topic(topic_parent):
    form = EditTopic()
    user = g.user

    if form.validate_on_submit():
        title = form.topicTitle.data
        parent = topic_parent
        tags = form.tags.data.replace(' ', '').split(',')
        description = form.description.data

        topic = UserTopic.query.filter_by(title=title,parent=parent).first()

        if title == parent:
            flash("Topic " +title+" cannot have the same name as parent "+parent)
            return render_template('create_new_topic.html', topic_parent=topic_parent, form=form)
        # if topic doesn'y already exist
        elif topic is None:
            topic = UserTopic(title, parent, tags, description)
            # Adds topic to DB and adds topic to list of user topics
            if topic.parent == user.username:
                g.user.topics.append(topic)
                db.session.add(g.user)

            db.session.add(topic)
            db.session.commit()

            flash("Topic "+title+" created succesfully!")
        else:
            flash("That topic already exists!")

        return redirect(url_for('topic', topic_name=title, topic_parent=parent))
    else:
        for error in form.errors:
            flash("Please enter a "+str(error)+" for "+topic_name)

    return render_template('create_new_topic.html', topic_parent=topic_parent, form=form)

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.route('/delete_topic/<parent_name>/<topic_name>')
@login_required
def delete_topic(parent_name,topic_name):
    topic = UserTopic.query.filter_by(title=topic_name, parent=parent_name).first()
    if topic:
        flash("Deleted topic "+topic.title+"!")
        

        # call get_subtopics here:
        # subtopics = UserTopic.query.filter_by(parent = )
        # delete all subtopics of topic to be deleted:


        db.session.delete(topic)
        db.session.commit()
    else:
        flash("That topic doesn't exist!")
    return redirect(url_for('home',username=g.user.username))

""" Recursively dig through subtopic tree and return all subtopics of all
    subtopics of the topic to be deleted.                               """
def get_subtopics():
    pass
