import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

CSRF_ENABLED = True
SECRET_KEY = 'PKB_is_da_shit'

# captcha config
RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = '6Lc7KfwSAAAAAO2ewgfog50aM8yr8RpPzrQNsg_e'
RECAPTCHA_PRIVATE_KEY = '6Lc7KfwSAAAAAPUFrcSIZgbYWaAlDyXN7EfXZFqT'
RECAPTCHA_OPTIONS = {'theme': 'white'}

# Flask-Mail config 
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
#MAIL_USE_TLS = True
MAIL_USERNAME = 'statesinfinite@gmail.com'
MAIL_PASSWORD = 'Buzzlightyear5'
MAIL_DEBUG = False
MAIL_FAIL_SILENTLY = True
MAIL_DEFAULT_SENDER = '"PKBMailer" <noreply@PKB.com>'


USER_PRODUCT_NAME = "PKB"
USER_ENABLE_USERNAME = True
