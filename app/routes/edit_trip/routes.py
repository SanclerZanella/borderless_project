from flask import (Blueprint, render_template,
                   session, request, flash,
                   redirect, url_for)
from bson.objectid import ObjectId
import datetime as dt
import cloudinary
import cloudinary.uploader
import cloudinary.api
from app.utils import (users_collections, trips_collection,
                       User, Trip)
from app.config import Config


# Configure Cloudinary API
cloudinary.config(
    cloud_name=Config.CLOUD_NAME,
    api_key=Config.API_KEY,
    api_secret=Config.API_SECRET,
    secure=True
)


# Flask Blueprint
edit_trip_pag = Blueprint("edit_trip", __name__)


@edit_trip_pag.route('/edit_trip/<trip_id>', methods=['GET', 'POST'])
def edit_trip(trip_id):
    """
    View to edit a trip
    """

    try:
        current_trip = trips_collection.find_one({'_id': ObjectId(trip_id)})
        current_catg = current_trip['trip_category'].lower()
        current_name = current_trip['trip_name'].lower()
        current_user = session['user']
        search_exp = (current_trip['trip_name']).replace(" ", " AND ")
        trip_path = cloudinary.Search().expression(search_exp).execute()
        resources = trip_path['resources']

        # Instance of Trip Class
        trip_func = Trip(None, None, None,
                         None, None, None,
                         None, None, None,
                         None)

        if request.method == "POST":
            # Catch data from form into variables
            trip_category = request.form.get("trip_category").lower()
            trip_name = request.form.get("trip_name").lower()
            trip_place_name = request.form.get("trip_place_name")
            trip_country = request.form.get("trip_country")
            trip_description = request.form.get("trip_description")
            trip_startdate = dt.datetime.strptime(
                request.form.get("trip_startdate"), '%Y-%m-%d')
            trip_end_date = dt.datetime.strptime(
                request.form.get("trip_end_date"), '%Y-%m-%d')
            trip_photos = request.files.getlist('trip_photos')
            trip_privacy = request.form.get("trip_privacy")

            # Instance of Trip Class for POST request method
            trip_func = Trip(current_trip['user'],
                             None,
                             trip_category,
                             trip_name,
                             trip_place_name,
                             trip_country,
                             trip_description,
                             trip_startdate,
                             trip_end_date,
                             trip_privacy)

            # Handle trip update
            trip_func.edit_trip(current_catg,
                                current_name,
                                resources,
                                current_trip,
                                trip_photos)

            flash('Trip Updated')
            return redirect(url_for('profile.profile'))

        # Current user notifications
        current_user_id = session['user']
        current_user = users_collections.find_one(
            {'_id': ObjectId(current_user_id)})
        notifications = current_user['notifications']

        # Instance of User Class
        user_func = User(None, None, None, None)
    except KeyError:
        """
        Catch KeyError in case there is no session called 'user'
        and redirect to the feed page
        """

        return redirect(url_for('main.feed'))

    return render_template('edit_trip.html',
                           profile_pic=user_func.get_profile_pic,
                           current_user=current_user,
                           current_trip=current_trip,
                           countries=trip_func.countries(),
                           trip_path=trip_path,
                           img_url=trip_func.img_url,
                           notifications=notifications)
