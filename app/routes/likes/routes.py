from flask import (Blueprint, session, jsonify,
                   redirect, url_for)
from bson.objectid import ObjectId
from app.utils import (trips_collection, Trip)


# Flask Blueprint
likes_func = Blueprint("likes", __name__)


@ likes_func.route('/likes/<trip_id>', methods=["GET", "POST"])
def likes(trip_id):
    """
    Count likes
    """

    try:
        # Instance of Trip Class
        trip_func = Trip(None, None, None,
                         None, None, None,
                         None, None, None,
                         None)

        current_user = session['user']
        trip = trips_collection.find_one({'_id': ObjectId(trip_id)})
        likes = trip['trip_likes']

        # Handle likes counting
        like_icon, count_likes = trip_func.like(current_user,
                                                trip_id,
                                                trip,
                                                likes)

        return jsonify({'result': 'success',
                        'current_user': current_user,
                        'trip_id': trip_id,
                        'like_icon': like_icon,
                        'count_likes': count_likes})
    except KeyError:
        """
        Catch KeyError in case there is no session called 'user'
        and redirect to the feed page
        """

        return redirect(url_for('main.feed'))
