from flask import (Blueprint, session,
                   jsonify, redirect,
                   url_for)
from bson.objectid import ObjectId
from app.utils import (users_collections, User)


# Flask Blueprint
follow_request_func = Blueprint("follow_request", __name__)


@follow_request_func.route("/follow_request/<user_id>",
                           methods=["POST", "GET"])
def follow_request(user_id):
    """
    Follow request
    """

    try:
        # Instance of User Class
        user_func = User(None, None, None, None)

        # Current user
        current_user = users_collections.find_one(
            {'_id': ObjectId(session['user'])})

        # Current user's followers
        rqt_current_user = current_user['followers']

        # Any user who was requested to be friend
        user = users_collections.find_one(
            {'_id': ObjectId(user_id)})

        # Handle follow request
        flwn_count = user_func.follow_request(current_user,
                                              rqt_current_user,
                                              user,
                                              user_id)

        return jsonify({
            'result': 'success',
            'user': user_id,
            'flwn_count': flwn_count
        })
    except KeyError:
        """
        Catch KeyError in case there is no session called 'user'
        and redirect to the feed page
        """

        return redirect(url_for('main.feed'))
