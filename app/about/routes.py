from flask import (Blueprint, render_template)


# Flask Blueprint
about_page = Blueprint("about", __name__)


@about_page.route("/about", methods=["GET", "POST"])
def about():
    """
    View to open the about page
    """

    return render_template("landpage.html")
