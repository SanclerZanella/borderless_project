from flask import (Blueprint, render_template,
                   session, request)
from bson.objectid import ObjectId
from app.utils import (users_collections, trips_collection,
                       Pagination, User, Trip)


# Flask Blueprint
public_profile_pag = Blueprint("public_profile", __name__)


@ public_profile_pag.route('/public_profile/<trip_user>',
                           methods=["GET", "POST"])
def public_profile(trip_user):
    """
    Public profile view
    """

    # Instance of User Class
    user_func = User(None, None, None, None)

    # Instance of Trip Class
    trip_func = Trip(None, None, None,
                     None, None, None,
                     None, None, None,
                     None)

    # Any user data
    user = users_collections.find_one({'_id': ObjectId(trip_user)})

    # Pagination
    db = trips_collection
    db_field = 'user'
    db_field_data = ObjectId(trip_user)
    sort_data = 'trip_startdate'
    sort_direction = -1
    pag_name = "public_profile"
    sec_arg = trip_user
    offset_sum = 5
    query_page = 'public_profile.public_profile'
    path = "/public_profile/%s" % trip_user

    if request.method == "POST":
        if request.args:
            offset = int(request.args['offset'])
            limit = int(request.args['limit'])
            page = int(request.args['page'])
            query = request.args['query']

            pprofile_pag = Pagination(db,
                                      db_field,
                                      db_field_data,
                                      sort_data,
                                      sort_direction,
                                      offset,
                                      limit,
                                      query)
        else:
            query = request.form.get('query')

            offset = 0
            limit = 5
            page = 1

            pprofile_pag = Pagination(db,
                                      db_field,
                                      db_field_data,
                                      sort_data,
                                      sort_direction,
                                      offset,
                                      limit,
                                      query)

        trips_pag = pprofile_pag.pag_data()
        num_pages = pprofile_pag.num_pages()
        prev_pag = pprofile_pag.pag_link('public_profile',
                                         trip_user,
                                         limit,
                                         (offset - limit),
                                         (page - 1))
        next_pag = pprofile_pag.pag_link('public_profile',
                                         trip_user,
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

            pprofile_pag = Pagination(db,
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

            pprofile_pag = Pagination(db,
                                      db_field,
                                      db_field_data,
                                      sort_data,
                                      sort_direction,
                                      offset,
                                      limit,
                                      query)

        trips_pag = pprofile_pag.pag_data()
        num_pages = pprofile_pag.num_pages()
        prev_pag = pprofile_pag.pag_link('public_profile',
                                         trip_user,
                                         limit,
                                         (offset - limit),
                                         (page - 1))
        next_pag = pprofile_pag.pag_link('public_profile',
                                         trip_user,
                                         limit,
                                         (offset + limit),
                                         (page + 1))

    # Get notifications for the current user
    if session.get('user'):
        current_user_id = session['user']
        current_user = users_collections.find_one(
            {'_id': ObjectId(current_user_id)})
        notifications = current_user['notifications']
        current_user_followers = current_user['followers']
    else:
        notifications = None
        current_user_followers = None

    # Public profile user
    user_ntf = user['notifications']
    user_followers = user['followers']
    user_following = user['following']

    ntf_id = []
    for ntf in range(len(user_ntf)):
        ntf_id.append(user_ntf[ntf]['_id'])

    # Statistics
    ctr, plc, days, long, ph = trip_func.statistics(trip_user)

    return render_template('public_profile.html',
                           profile_pic=user_func.get_profile_pic,
                           user_photo=trip_func.user_post_photo,
                           cover_pic=user_func.get_cover_pic,
                           bg_post_url=trip_func.get_BGPost_pic,
                           no_files=trip_func.get_no_pictures,
                           query_page=query_page,
                           path=path,
                           trips=trips_pag,
                           user=user,
                           full_name=user_func.get_full_name,
                           num_pages=num_pages,
                           limit=limit,
                           offset=offset,
                           page=page,
                           prev_pag=prev_pag,
                           next_pag=next_pag,
                           pag_link=pprofile_pag.pag_link,
                           pag_name=pag_name,
                           sec_arg=sec_arg,
                           offset_sum=offset_sum,
                           notifications=notifications,
                           ntf_id=ntf_id,
                           user_followers=user_followers,
                           user_following=user_following,
                           current_user_followers=current_user_followers,
                           num_coun=ctr,
                           num_plc=plc,
                           total_days=days,
                           long_day=long,
                           total_photos=ph)
