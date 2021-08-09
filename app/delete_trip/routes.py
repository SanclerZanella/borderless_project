from flask import (Blueprint, request,
                   flash, redirect)
from bson.objectid import ObjectId
import cloudinary
import cloudinary.uploader
import cloudinary.api
from app.utils import (trips_collection, Trip)
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

    # Instance of Trip Class
    trip_func = Trip(None, None, None,
                     None, None, None,
                     None, None, None,
                     None)

    trip = trips_collection.find_one({'_id': ObjectId(trip_id)})
    search_exp = (trip['trip_name']).replace(" ", " AND ")
    trip_path = cloudinary.Search().expression(search_exp).execute()

    # Handle trip deletion
    trip_func.delete_trip(trip, trip_path, trip_id)

    flash("Trip Successfuly Deleted")
    return redirect(request.referrer)
