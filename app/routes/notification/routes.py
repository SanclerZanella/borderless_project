from flask import (Blueprint, session,
                   jsonify)
from bson.objectid import ObjectId
from app.utils import (users_collections, User)


# Flask Blueprint
notification_func = Blueprint("notification", __name__)


@notification_func.route("/notification/<user_id>",
                         methods=["POST", "GET"])
def notification(user_id):
    """
    Notifications
    """

    # Instance of User Class
    user_func = User(None, None, None, None)

    # Current user
    current_user = users_collections.find_one(
        {'_id': ObjectId(session['user'])})

    # Any user who was requested to be friend
    user = users_collections.find_one(
        {'_id': ObjectId(user_id)})
    # User notifications
    ntf_user = user['notifications']

    # Handle notification functionality
    user_func.notification(current_user, user, ntf_user, user_id)

    return jsonify({'result': 'success'})
