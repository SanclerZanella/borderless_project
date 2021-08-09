from flask import Blueprint, render_template


# Flask Blueprint
errors = Blueprint("errors", __name__)


"""
App routes
"""


@errors.errorhandler(500)
def error_500(error):
    """
    Handle 500 Internal Server error
    """

    return render_template("erros/500.html"), 500


@errors.errorhandler(404)
def error_404(error):
    """
    Handle 404 not found error
    """

    return render_template("erros/404.html"), 404
