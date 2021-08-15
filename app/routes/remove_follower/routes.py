from flask import (Blueprint, jsonify,
                   redirect, url_for)
from app.utils import (User)


# Flask Blueprint
remove_follower_func = Blueprint("remove_follower", __name__)


@remove_follower_func.route("/remove_follower/<user_id>",
                            methods=["POST", "GET"])
def remove_follower(user_id):
    """
    Remove user's follower
    """

    try:
        # Instance of User Class
        user_func = User(None, None, None, None)

        # Remove follower from database
        followers_count = user_func.remove_follower(user_id)

        return jsonify({
            'result': 'success',
            'count_flwr': followers_count,
        })
    except KeyError:
        """
        Catch KeyError in case there is no session called 'user'
        and redirect to the feed page
        """

        return redirect(url_for('main.feed'))
