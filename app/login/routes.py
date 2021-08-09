from flask import (Blueprint, session,
                   request, flash,
                   redirect, url_for)
from app.utils import User


# Flask Blueprint
login_func = Blueprint("login", __name__)


@login_func.route("/login", methods=["GET", "POST"])
def login():
    """
    View to handle the login form modal
    """

    if request.method == "POST":

        # Instance of User Class
        user_func = User(None,
                         None,
                         request.form.get("emailL"),
                         request.form.get("passwordL"))

        # Return if the user exists and if the password matches
        existing_user, password, user = user_func.login()

        # Check if the user exists and if the password matches
        if existing_user:
            if password:

                # Put the user into 'session' cookie
                session["user"] = str(user["_id"])

                # redirect to user's profile
                flash("Welcome, {}".format(
                    user["fname"].capitalize()))
                return redirect(url_for("profile.profile"))

            else:
                # Invalid password
                flash("Incorrect username and/or password")
                return redirect(request.referrer)

        else:
            # Username doesn't exist
            flash("Incorrect email and/or password")
            return redirect(request.referrer)

    # If the user does not exist or the password does not match,
    # redirect to previous page
    return redirect(request.referrer)
