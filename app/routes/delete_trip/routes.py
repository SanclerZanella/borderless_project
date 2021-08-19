from flask import (Blueprint, request,
                   flash, redirect,
                   url_for)
import cloudinary
import cloudinary.uploader
import cloudinary.api
from app.utils import Trip
from app.config import Config

# Configure Cloudinary API
cloudinary.config(
    cloud_name=Config.CLOUD_NAME,
    api_key=Config.API_KEY,
    api_secret=Config.API_SECRET,
    secure=True
)


# Flask Blueprint
delete_trip_func = Blueprint("delete_trip", __name__)


@delete_trip_func.route('/delete_trip/<trip_id>')
def delete_trip(trip_id):
    """
    View to execute the delete_trip
    """

    try:
        # Instance of Trip Class
        trip_func = Trip(None, None, None,
                         None, None, None,
                         None, None, None,
                         None)

        # Handle trip deletion
        trip_func.delete_trip(trip_id)

        flash("Trip Successfuly Deleted")
        return redirect(request.referrer)

    except KeyError:
        """
        Catch KeyError in case there is no session called 'user'
        and redirect to the feed page
        """

        return redirect(url_for('main.feed'))
