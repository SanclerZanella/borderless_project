from flask import Flask
import jinja_partials
from flask_pymongo import PyMongo
import cloudinary
import cloudinary.uploader
import cloudinary.api
from app.config import Config

# Reusable extension for PyMongo
mongo = PyMongo()

# Configure Cloudinary API
cloudinary.config(
    cloud_name=Config.CLOUD_NAME,
    api_key=Config.API_KEY,
    api_secret=Config.API_SECRET,
    secure=True
)

map_key = Config.MAP_KEY


def create_app(config_class=Config):
    """
    Create entire instance of the app
    """

    # app initialization and configuration
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register Partials method
    jinja_partials.register_extensions(app)

    # extensions for app init from above
    mongo.init_app(app)

    # route imports
    from app.errors.routes import errors
    from app.main.routes import main
    from app.about.routes import about_page
    from app.delete_img.routes import delete_img_func
    from app.delete_trip.routes import delete_trip_func
    from app.edit_profile.routes import edit_profile_page
    from app.edit_trip.routes import edit_trip_pag
    from app.follow_request.routes import follow_request_func
    from app.likes.routes import likes_func
    from app.login.routes import login_func
    from app.logout.routes import logout_func
    from app.notification.routes import notification_func
    from app.profile.routes import profile_pag
    from app.public_profile.routes import public_profile_pag
    from app.remove_follower.routes import remove_follower_func
    from app.signup.routes import signup_func
    from app.trip.routes import trip_pag

    app.register_blueprint(errors)
    app.register_blueprint(main)
    app.register_blueprint(about_page)
    app.register_blueprint(delete_img_func)
    app.register_blueprint(delete_trip_func)
    app.register_blueprint(edit_profile_page)
    app.register_blueprint(edit_trip_pag)
    app.register_blueprint(follow_request_func)
    app.register_blueprint(likes_func)
    app.register_blueprint(login_func)
    app.register_blueprint(logout_func)
    app.register_blueprint(notification_func)
    app.register_blueprint(profile_pag)
    app.register_blueprint(public_profile_pag)
    app.register_blueprint(remove_follower_func)
    app.register_blueprint(signup_func)
    app.register_blueprint(trip_pag)

    return app
