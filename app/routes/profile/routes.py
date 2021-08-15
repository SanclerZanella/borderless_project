from flask import (Blueprint, render_template,
                   session, request, flash,
                   redirect, url_for)
from bson.objectid import ObjectId
import datetime as dt
from app.utils import (users_collections, trips_collection,
                       Pagination, User, Trip)


# Flask Blueprint
profile_pag = Blueprint("profile", __name__)


@profile_pag.route("/profile", methods=["GET", "POST"])
def profile():
    """
    View to execute the profile page
    (Add new trip button, feed to show the trips, followers,
    following and statistics)
    """

    try:
        # Instance of User Class
        user_func = User(None, None, None, None)

        # Instance of Trip Class
        trip_func = Trip(None, None, None,
                         None, None, None,
                         None, None, None,
                         None)

        # Current user
        current_user = users_collections.find_one(
            {'_id': ObjectId(session['user'])})

        # Current user ID
        current_user_id = current_user['_id']

        # Pagination
        db = trips_collection
        db_field = 'user'
        db_field_data = current_user_id
        sort_data = 'trip_startdate'
        sort_direction = -1
        pag_name = 'profile'
        sec_arg = None
        offset_sum = 5
        query_page = 'profile.profile'
        path = "/public_profile/%s" % session['user']

        if request.method == "POST":

            # Catch data from form into variables
            trip_category = request.form.get("trip_category")

            if trip_category is not None:

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
                trip_func = Trip(current_user_id,
                                 current_user['fname'],
                                 trip_category,
                                 trip_name,
                                 trip_place_name,
                                 trip_country,
                                 trip_description,
                                 trip_startdate,
                                 trip_end_date,
                                 trip_privacy)

                trip_func.new_trip()

                trip_func.cloud_folder(trip_photos)

                flash('Trip successfully added')

                # Search query
                query = request.form.get('query')

                if request.args:
                    offset = int(request.args['offset'])
                    limit = int(request.args['limit'])
                    page = int(request.args['page'])
                    query = request.args['query']

                    profile_pag = Pagination(db,
                                             db_field,
                                             db_field_data,
                                             sort_data,
                                             sort_direction,
                                             offset,
                                             limit,
                                             query)
                else:
                    offset = 0
                    limit = 5
                    page = 1

                    profile_pag = Pagination(db,
                                             db_field,
                                             db_field_data,
                                             sort_data,
                                             sort_direction,
                                             offset,
                                             limit,
                                             query)

                trips_pag = profile_pag.pag_data()
                num_pages = profile_pag.num_pages()
                prev_pag = profile_pag.pag_link('profile',
                                                None,
                                                limit,
                                                (offset - limit),
                                                (page - 1))
                next_pag = profile_pag.pag_link('profile',
                                                None,
                                                limit,
                                                (offset + limit),
                                                (page + 1))

            else:
                # Search query
                query = request.form.get('query')

                if request.args:
                    offset = int(request.args['offset'])
                    limit = int(request.args['limit'])
                    page = int(request.args['page'])
                    query = request.args['query']

                    profile_pag = Pagination(db,
                                             db_field,
                                             db_field_data,
                                             sort_data,
                                             sort_direction,
                                             offset,
                                             limit,
                                             query)
                else:
                    offset = 0
                    limit = 5
                    page = 1

                    profile_pag = Pagination(db,
                                             db_field,
                                             db_field_data,
                                             sort_data,
                                             sort_direction,
                                             offset,
                                             limit,
                                             query)

                trips_pag = profile_pag.pag_data()
                num_pages = profile_pag.num_pages()
                prev_pag = profile_pag.pag_link('profile',
                                                None,
                                                limit,
                                                (offset - limit),
                                                (page - 1))
                next_pag = profile_pag.pag_link('profile',
                                                None,
                                                limit,
                                                (offset + limit),
                                                (page + 1))
        elif request.method == "GET":
            if request.args:
                offset = int(request.args['offset'])
                limit = int(request.args['limit'])
                page = int(request.args['page'])

                if 'query' in request.args:
                    query = request.args['query']
                else:
                    query = None

                profile_pag = Pagination(db,
                                         db_field,
                                         db_field_data,
                                         sort_data,
                                         sort_direction,
                                         offset,
                                         limit,
                                         query)
            else:
                offset = 0
                limit = 5
                page = 1
                query = None

                profile_pag = Pagination(db,
                                         db_field,
                                         db_field_data,
                                         sort_data,
                                         sort_direction,
                                         offset,
                                         limit,
                                         query)

            trips_pag = profile_pag.pag_data()
            num_pages = profile_pag.num_pages()
            prev_pag = profile_pag.pag_link('profile',
                                            None,
                                            limit,
                                            (offset - limit),
                                            (page - 1))
            next_pag = profile_pag.pag_link('profile',
                                            None,
                                            limit,
                                            (offset + limit),
                                            (page + 1))

        # Verify if the user has trips recorded
        user_trips = []
        if len(profile_pag.all_data()):
            for trip in profile_pag.all_data():
                user_trips.append(trip)

        # Get current user's notifications
        notifications = current_user['notifications']

        # Get current user's friends
        user_followers = current_user['followers']
        user_following = current_user['following']

        # Statistics
        ctr, plc, days, long, ph = trip_func.statistics(session['user'])
    except KeyError:
        """
        Catch KeyError in case there is no session called 'user'
        and redirect to the feed page
        """

        return redirect(url_for('main.feed'))

    return render_template('profile.html',
                           countries=trip_func.countries(),
                           trips=trips_pag,
                           query_page=query_page,
                           path=path,
                           full_name=user_func.get_full_name,
                           current_user_id=current_user_id,
                           user_trips=user_trips,
                           profile_pic=user_func.get_profile_pic,
                           user_photo=trip_func.user_post_photo,
                           cover_pic=user_func.get_cover_pic,
                           bg_post_url=trip_func.get_BGPost_pic,
                           no_files=trip_func.get_no_pictures,
                           num_pages=num_pages,
                           limit=limit,
                           offset=offset,
                           page=page,
                           prev_pag=prev_pag,
                           next_pag=next_pag,
                           pag_link=profile_pag.pag_link,
                           pag_name=pag_name,
                           sec_arg=sec_arg,
                           offset_sum=offset_sum,
                           notifications=notifications,
                           followers=user_followers,
                           following=user_following,
                           num_coun=ctr,
                           num_plc=plc,
                           total_days=days,
                           long_day=long,
                           total_photos=ph)
