from app import app, db, login_manager
from flask import render_template, flash, redirect, session, url_for, request, g
from app.models import User
from app.forms import LoginForm, RegisterForm
from flask.ext.login import login_user, logout_user, current_user, login_required

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
@app.route('/')
@app.route('/home', methods=['GET'])
def home():
	#return "THIS IS PKB BITCHEzzz"
    return render_template('home.html')

@app.route('/register' , methods=['GET','POST'])
def register():
    # if user is logged in, redirect them to index
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = RegisterForm()
    # tries to register user
    if form.validate_on_submit():
        new_user = User.query.filter_by(username=form.username.data).first()
        if new_user is None:
            user = User(form.username.data, form.password.data)

            # makes directory to store files on
            directory = os.path.join(app.config['UPLOAD_FOLDER'], 'Teams', form.username.data)
            if not os.path.exists(directory):
                os.makedirs(directory)

            db.session.add(user)

            # creates UserFile objects to represent team submissions
            for i in range(30):
                user_file = UserFile(
                    problem_number=i+1,
                    status="Not Submitted",
                    timestamp = datetime.utcnow(),
                    team = user)
                db.session.add(user_file)

            db.session.commit()

            flash('User successfully registered')
            return redirect(url_for('login'))
        else:
            form.username.errors.append('That username is already taken!')
    return render_template('register.html', form = form)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    # if user is logged in, redirect them to index
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
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
                return redirect(request.args.get('next') or url_for('index'))
            else:
                form.password.errors.append("Invalid password!")
        else:
            form.username.errors.append("Invalid username!")
    return render_template('login.html', title = 'Sign In', form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))