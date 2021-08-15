from flask import (Blueprint, jsonify,
                   redirect, url_for)
from app.utils import Trip


# Flask Blueprint
delete_img_func = Blueprint("delete_img", __name__)


@delete_img_func.route('/delete_img/<trip_id>/<filename>',
                       methods=["GET", "POST"])
def delete_img(trip_id, filename):
    """
    Delete one image from cloud platform
    """

    try:
        # Instance of Trip Class
        trip_func = Trip(None, None, None,
                         None, None, None,
                         None, None, None,
                         None)

        # Handle image deletion
        trip_func.delete_img(trip_id, filename)

        return jsonify({'result': 'success'})
    except KeyError:
        """
        Catch KeyError in case there is no session called 'user'
        and redirect to the feed page
        """

        return redirect(url_for('main.feed'))
