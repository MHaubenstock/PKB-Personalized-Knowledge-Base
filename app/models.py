from app import db
from werkzeug.security import generate_password_hash, check_password_hash

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    pwd_hash = db.Column(db.String(64))
    score = db.Column(db.Integer, default = 0)
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    files = db.relationship('UserFile', backref = 'team', lazy = 'dynamic')

    def __init__(self, username, password, role=ROLE_USER):
        self.username = username
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