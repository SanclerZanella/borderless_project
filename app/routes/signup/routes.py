from flask import (Blueprint, session,
                   request, redirect,
                   flash, url_for)
from app.utils import (users_collections, User)


# Flask Blueprint
signup_func = Blueprint("signup", __name__)


@signup_func.route("/signup", methods=["GET", "POST"])
def signup():
    """
    View to handle the sign up form modal
    """

    if request.method == "POST":

        # Instance of User Class
        user_func = User(request.form.get("fname"),
                         request.form.get("lname"),
                         request.form.get("email"),
                         request.form.get("password"))

        # Check if the username already exists in db
        existing_user = users_collections.find_one(
            {"email": request.form.get("email")})

        if existing_user:
            flash("User already exists")

            # redirect to previous page if the users already exists
            return redirect(request.referrer)

        # Register the user in DB
        user_func.register_user()

        # Fetch the new user in DB
        registered_user = users_collections.find_one(
            {"email": request.form.get("email")})

        # Put the new user into 'session' cookie
        session['user'] = str(registered_user["_id"])

        # Create user's folder in cloud platform
        user_func.cloud_folder(session['user'])

        # Redirect to the new user's profile
        flash("Registration Successful")
        return redirect(url_for("profile.profile"))
