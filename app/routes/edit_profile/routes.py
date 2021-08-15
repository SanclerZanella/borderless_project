from flask import (Blueprint, render_template,
                   session, request, flash,
                   redirect, url_for)
from bson.objectid import ObjectId
from app.utils import (users_collections, User)


# Flask Blueprint
edit_profile_page = Blueprint("edit_profile", __name__)


@edit_profile_page.route('/edit_profile', methods=["POST", "GET"])
def edit_profile():
    """
    View to edit profile
    """

    try:
        current_user = users_collections.find_one(
            {'_id': ObjectId(session['user'])})

        if request.method == 'POST':

            # Instance of User Class (POST request)
            user_func = User(request.form.get('fname'),
                             request.form.get('lname'),
                             None, None)

            # Update profile and cover pictures in cloud platform
            profile_photo = request.files['profile_photo']
            if profile_photo.filename != "":
                user_func.update_profile_pic(profile_photo)

            cover_photo = request.files['cover_photo']
            if cover_photo.filename != "":
                user_func.update_cover_pic(cover_photo)

            # Update name in DB
            user_func.update_name()

            # Redirect to profile page after update
            flash('Profile Updated')
            return redirect(url_for('profile.profile'))

        # Instance of User Class (GET request)
        user_func = User(None, None, None, None)

        # Get current user's notifications
        notifications = current_user['notifications']
    except KeyError:
        """
        Catch KeyError in case there is no session called 'user'
        and redirect to the feed page
        """

        return redirect(url_for("main.feed"))

    return render_template("edit_profile.html",
                           profile_pic=user_func.get_profile_pic,
                           cover_pic=user_func.get_cover_pic,
                           current_user=current_user,
                           notifications=notifications)
