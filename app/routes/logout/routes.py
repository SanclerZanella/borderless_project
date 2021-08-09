from flask import (Blueprint, flash,
                   redirect, url_for)
from app.utils import User


# Flask Blueprint
logout_func = Blueprint("logout", __name__)


@logout_func.route("/logout")
def logout():
    """
    View to logout the user (Clear the session cookie)
    """

    # Instance of User Class
    user_func = User(None, None, None, None)

    # Logout user
    user_func.logout()

    # Remove user from session cookie
    flash("You have been logged out")
    return redirect(url_for("main.feed"))
