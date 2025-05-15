from flask_caching import Cache
from flask_cors import CORS
from flask_mail import Mail
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

api = Api()
cache = Cache()
cors = CORS()
csrf = CSRFProtect()
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
