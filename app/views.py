from app import app, db, login_manager
from flask import render_template, flash, redirect, session, url_for, request, g
from app.models import User
from app.models import UserTopic
from app.forms import LoginForm, RegisterForm, EditTopic, PasswordResetForm
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

    if form.validate_on_submit():
        print("stuff:",form.topicTitle.data, form.description.data)
        if form.topicTitle.data and form.description.data:
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
                flash("Please enter a "+str(error)+" for "+form.topicTitle.data)

    form.topicTitle.data = topic.title
    form.description.data = topic.description
    form.tags.data = ', '.join([str(tag) for tag in topic.tags])

    return render_template('edittopic.html', topic=topic, form=form)

@app.route('/<topic_parent>/create_new_topic', methods = ['GET', 'POST'])
@login_required
def create_new_topic(topic_parent):
    form = EditTopic()
    user = g.user

    if form.validate_on_submit():

        # collects topic attributes from form
        title = form.topicTitle.data
        parent = topic_parent
        # users must enter tags with commas separating
        tags = form.tags.data.replace(' ', '').split(',')
        description = form.description.data

        if title == parent:
            flash("Topic " +title+" cannot have the same name as parent "+parent)
            return render_template('create_new_topic.html', topic_parent=topic_parent, form=form)

        # queries database for topic to see if it exists
        topic = UserTopic.query.filter_by(title=title,parent=parent).first()

        # if no topic exists in the database
        if topic is None:
            topic = UserTopic(title, parent, tags, description)

            # if topic is high level topic, add to user's list of topics
            if topic.parent == user.username:
                g.user.topics.append(topic)
                topic.user = user

            db.session.add(topic)
            db.session.commit()

            flash("Topic "+title+" created succesfully!")
            return redirect(url_for("topic", topic_name=title, topic_parent=parent))
        else:
            flash("That topic already exists!")

    return render_template('create_new_topic.html', topic_parent=topic_parent, form=form)

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.route('/delete_topic/<parent_name>/<topic_name>')
@login_required
def delete_topic(parent_name,topic_name):
    topic = UserTopic.query.filter_by(title=topic_name, parent=parent_name).first()
    if topic:
        # deletes all subtopics from db first 
        delete_subtopics(topic)
        # deletes topic from db
        db.session.delete(topic)
        db.session.commit()
        flash("Deleted topic "+topic.title+"!")
    else:
        flash("That topic doesn't exist!")
    return redirect(url_for('home',username=g.user.username))

""" Recursively dig through subtopic tree and return all subtopics of all
    subtopics of the topic to be deleted.                               """
def delete_subtopics(topic):
    subtopics = UserTopic.query.filter_by(parent=topic.title).all()
    if subtopics:
        for subtopic in subtopics:
            delete_subtopics(subtopic)
            try:
                db.session.delete(subtopic)
            except:
                flash("Could not delete", subtopic.title)


@app.route('/recovery')
def password_recovery_request():
	return render_template('/recovery.html')

@app.route('/recovery', methods=['POST'])
def account_key_generator():
	# Complete the request to generate a new password-reset key
	# and send it to the provided email if it is valid

	# Check to see if email exists
	if not request.form.get('email'):
		flash('Email does not exist, check the field and try again.')
		return redirect(url_for('app.password_recovery_request'))
	# Delete key if there was already one in place.
	existing_keys = UserMeta.query.filter_by(key='password_rec_key', user_id=user.id)
	if existing_keys:
		for key in existing_keys:
			deb.session.delete(key)

	# Generate a password recovery key
	key = str(random.getrandbits(128))
	user.user_meta = [UserMeta(key='password_rec_key', val=key)]

	# Send the email with key to user.
	send('password_recovery', 'Password Recovery', [user.email], user=user, key=key)

	flash('An email has been sent! Please check your inbox and follow the instructions to complete your password reset.')
	return redirect(url_for('login'))

@app.route('/search/<tag>')
def search(tag):
    user = g.user

    # can't think of a good way to query db for 
    # tags so this will have to do:
    user_topics = collect_topics(user.username)
    topics_with_tag = []

    for topic in user_topics:
        for t_tag in topic.tags:
            if t_tag == tag:
                topics_with_tag.append(topic)

    return render_template("search.html", topics=topics_with_tag, tag=tag)

def collect_topics(parent):
    subtopics = UserTopic.query.filter_by(parent=parent).all()
    if not subtopics:
        return []
    results = []
    for subtopic in subtopics:
        results.append(subtopic)
        results += collect_topics(subtopic.title)
    return results