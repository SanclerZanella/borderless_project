from flask import (Blueprint, render_template,
                   session)
from bson.objectid import ObjectId
from app.config import Config
from app.utils import (users_collections, trips_collection,
                       User, Trip)


# Flask Blueprint
trip_pag = Blueprint("trip", __name__)


@trip_pag.route('/trip/<trip_id>', methods=["GET", "POST"])
def trip(trip_id):
    """
    View to open the trip post
    """

    # Instance of Trip Class
    trip_func = Trip(None, None, None,
                     None, None, None,
                     None, None, None,
                     None)

    trip = trips_collection.find_one({'_id': ObjectId(trip_id)})
    resources = trip_func.folder_resources(trip_id)

    num_photos = trip_func.get_no_pictures(trip['user'], trip['_id'])
    map = Config.MAP_KEY

    if session.get('user'):
        current_user_id = session['user']
        current_user = users_collections.find_one(
            {'_id': ObjectId(current_user_id)})
        notifications = current_user['notifications']
    else:
        notifications = None

    # Instance of User Class
    user_func = User(None, None, None, None)

    return render_template('trip.html',
                           trip=trip,
                           profile_pic=user_func.get_profile_pic,
                           resources=resources,
                           img_url=trip_func.img_url,
                           map=map,
                           num_photos=num_photos,
                           notifications=notifications)
