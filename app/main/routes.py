from flask import (Blueprint, render_template,
                   session, request)
from bson.objectid import ObjectId
from app.utils import (users_collections, trips_collection,
                       Pagination, User, Trip)


# Flask Blueprint
main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def feed():
    """
    View for landpage
    """

    if session.get('user'):
        # Current user
        current_user = users_collections.find_one(
            {'_id': ObjectId(session['user'])})

        # Current user ID
        current_user_id = current_user['_id']

        notifications = current_user['notifications']
    else:
        current_user_id = None
        notifications = None

    # Pagination
    db = trips_collection
    db_field = None
    db_field_data = None
    sort_data = '_id'
    sort_direction = -1

    # Search query
    if request.method == "POST":
        query = request.form.get('query')

        if request.args:
            offset = int(request.args['offset'])
            limit = int(request.args['limit'])
            page = int(request.args['page'])
            query = request.args['query']

            feed_pag = Pagination(db,
                                  db_field,
                                  db_field_data,
                                  sort_data,
                                  sort_direction,
                                  offset,
                                  limit,
                                  query)
        else:
            offset = 0
            limit = 10
            page = 1

            feed_pag = Pagination(db,
                                  db_field,
                                  db_field_data,
                                  sort_data,
                                  sort_direction,
                                  offset,
                                  limit,
                                  query)

        trips_pag = feed_pag.all_data()
        num_pages = feed_pag.num_pages()
        prev_pag = feed_pag.pag_link('',
                                     None,
                                     limit,
                                     (offset - limit),
                                     (page - 1))
        next_pag = feed_pag.pag_link('',
                                     None,
                                     limit,
                                     (offset + limit),
                                     (page + 1))

    else:
        if request.args:
            offset = int(request.args['offset'])
            limit = int(request.args['limit'])
            page = int(request.args['page'])

            if 'query' in request.args:
                query = request.args['query']
            else:
                query = None

            feed_pag = Pagination(db,
                                  db_field,
                                  db_field_data,
                                  sort_data,
                                  sort_direction,
                                  offset,
                                  limit,
                                  query)
        else:
            offset = 0
            limit = 10
            page = 1
            query = None

            feed_pag = Pagination(db,
                                  db_field,
                                  db_field_data,
                                  sort_data,
                                  sort_direction,
                                  offset,
                                  limit,
                                  query)

        trips_pag = feed_pag.all_data()
        num_pages = feed_pag.num_pages()
        prev_pag = feed_pag.pag_link('',
                                     None,
                                     limit,
                                     (offset - limit),
                                     (page - 1))
        next_pag = feed_pag.pag_link('',
                                     None,
                                     limit,
                                     (offset + limit),
                                     (page + 1))

    # Instance of User Class
    user_func = User(None, None, None, None)

    # Instance of Trip Class
    trip_func = Trip(None, None, None,
                     None, None, None,
                     None, None, None,
                     None)

    return render_template("feed.html",
                           current_user_id=current_user_id,
                           trips=trips_pag,
                           bg_post_url=trip_func.get_BGPost_pic,
                           no_files=trip_func.get_no_pictures,
                           user_photo=trip_func.user_post_photo,
                           num_pages=num_pages,
                           limit=limit,
                           offset=offset,
                           page=page,
                           prev_pag=prev_pag,
                           next_pag=next_pag,
                           pag_link=feed_pag.pag_link,
                           notifications=notifications,
                           profile_pic=user_func.get_profile_pic)
