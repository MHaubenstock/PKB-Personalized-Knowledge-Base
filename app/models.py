from app import db
from werkzeug.security import generate_password_hash, check_password_hash

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    pwd_hash = db.Column(db.String(64))
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    topics = db.relationship('UserTopic', backref = 'user', lazy = 'dynamic')
    meta = db.relationship('UserMeta', backref = 'user', lazy = 'dynamic')
    email = db.Column(db.String(255), unique=True)
    confirmed_at = db.Column(db.DateTime())


    def __init__(self, username, email, password, role=ROLE_USER):
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role
        
    def set_password(self, password):
        self.pwd_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwd_hash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)

class UserMeta(db.Model):
        __tablename__ = 'user_meta'
        id = db.Column(db.Integer, primary_key=True)
        key = db.Column(db.String(16))
        val = db.Column(db.String(128))
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class UserTopic(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(40))
    description = db.Column(db.String(1000))
    parent = db.Column(db.String(40))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tags = db.Column(db.PickleType)
    
    def __init__(self, title, parent, tags=None, description=None):
        self.title = title
        self.parent = parent
        self.tags = tags
        self.description = description

