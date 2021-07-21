import os
import math
from flask import (Flask, flash,
                   render_template, redirect,
                   request, session, url_for,
                   jsonify)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import datetime as dt
import cloudinary
import cloudinary.uploader
import cloudinary.api
if os.path.exists('env.py'):
    import env


# Instance of Flask
app = Flask(__name__)

# Grab the database name
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")

# Configure the actual DB connection string
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

# Secret key required to connect to flash() and session()
# flask functions
app.secret_key = os.environ.get("SECRET_KEY")

# Create an instance of PyMongo
mongo = PyMongo(app)


# Configure Cloudinary API
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)


# Map API key
map_key = os.environ.get("MAP_KEY")


# Get image url from cloud
def img_url(folder, filename):
    pic_url = cloudinary.CloudinaryImage('%s/%s' % (folder,
                                                    filename)).url
    # return pic_url


# Get profile picture url
def get_profile_pic(user_id):
    current_user = mongo.db.users.find_one(
        {'_id': ObjectId(user_id)})
    current_user_id = current_user['_id']
    profile_folder_id = "default_profile_pic"
    profile_folder = "users/%s/profile/" % current_user_id
    profile_pic_path = "%s/%s" % (profile_folder, profile_folder_id)
    profile_pic_url = cloudinary.CloudinaryImage(profile_pic_path).url

    # return profile_pic_url


# Get cover picture url
def get_cover_pic(user_id):
    current_user = mongo.db.users.find_one(
        {'_id': ObjectId(user_id)})
    current_user_id = current_user['_id']
    cover_folder_id = "default_cover_pic"
    cover_folder = "users/%s/cover/" % current_user_id
    cover_pic_path = "%s/%s" % (cover_folder, cover_folder_id)
    cover_pic_url = cloudinary.CloudinaryImage(cover_pic_path).url

    # return cover_pic_url


# Get trip post link background picture url
def get_BGPost_pic(user_id, trip_id):
    post = mongo.db.trips.find_one(
        {'_id': ObjectId(trip_id)})
    num_pic = get_no_pictures(user_id, trip_id)

    if num_pic > 0:
        search_exp = (post['trip_name']).replace(" ", " AND ")
        trip_path = cloudinary.Search().expression(search_exp).execute()
        res = trip_path['resources'][-1]
        first_pic = res['public_id']
        post_BGpic_url = cloudinary.CloudinaryImage('%s.jpg' % first_pic).url
        # return post_BGpic_url
    else:
        local_img = '../static/images/default_post_cover.jpg'
        # return local_img


# Get number of pictures in a folder
def get_no_pictures(trip_user, trip_id):
    user = mongo.db.users.find_one(
        {'_id': ObjectId(trip_user)})
    current_user_id = user['_id']
    post = mongo.db.trips.find_one(
        {'_id': trip_id})

    if current_user_id == post['user']:
        search_exp = (post['trip_name']).replace(" ", " AND ")
        search_cloud = cloudinary.Search().expression(search_exp).execute()
        no_files = search_cloud['total_count']
        return no_files


# Update profile
def update_profile_pic(profile_photo):
    user_id = mongo.db.users.find_one(
        {"_id": ObjectId(session["user"])})
    default_profile_pic = profile_photo
    profile_folder_id = "default_profile_pic"
    profile_folder = "users/%s/profile/" % user_id['_id']

    cloudinary.uploader.upload(default_profile_pic,
                               folder=profile_folder,
                               public_id=profile_folder_id,
                               format='jpg',
                               overwrite=True,
                               invalidate=True,
                               use_filename=True)


# Update profile and cover pictures
def update_cover_pic(cover_photo):
    user_id = mongo.db.users.find_one(
        {"_id": ObjectId(session["user"])})
    default_cover_pic = cover_photo
    cover_folder_id = "default_cover_pic"
    cover_folder = "users/%s/cover/" % user_id['_id']

    cloudinary.uploader.upload(default_cover_pic,
                               folder=cover_folder,
                               public_id=cover_folder_id,
                               format='jpg',
                               overwrite=True,
                               invalidate=True,
                               use_filename=True)


# Get the profile photo of the post author
def user_post_photo(user_id):
    current_user = mongo.db.users.find_one(
        {'_id': ObjectId(user_id)})
    current_user_id = current_user['_id']
    profile_folder_id = "default_profile_pic"
    profile_folder = "users/%s/profile/" % current_user_id
    profile_pic_path = "%s/%s" % (profile_folder, profile_folder_id)
    profile_pic_url = cloudinary.CloudinaryImage(profile_pic_path).url

    return profile_pic_url


# Provide a list of all images in a trip folder in
# the cloud
def trip_folder_resources(trip_name):
    search_exp = (trip_name).replace(" ", " AND ")
    trip_path = cloudinary.Search().expression(search_exp).execute()
    resources = trip_path['resources']

    return resources


# Update trip photos in the cloud
def update_trip_photos(trip_photos,
                       resources,
                       trip_category,
                       trip_name,
                       current_user_id):

    # Check if there is any photo in the trip folder in the cloud
    if len(resources) > 0:

        # Check if the user uploaded any photo
        if trip_photos[0].filename != "":
            ids = []
            last_file = resources[0]['filename']
            last_file_id = int(last_file[-1])
            ids.append(last_file_id)

            # Send uploded photos to the cloud
            for trip_photo in range(len(trip_photos)):
                file = trip_photos[trip_photo]
                category = trip_category.lower().replace(" ", "_")
                folder_name = trip_name.replace(" ", "_").lower()

                last_id = ids[-1]
                id = last_id + 1
                ids.append(id)
                photo_id = "%s_%s" % (folder_name, id)

                folder_path = "users/%s/trips/%s/%s/" % (current_user_id,
                                                         category,
                                                         folder_name)
                cloudinary.uploader.upload(file,
                                           folder=folder_path,
                                           public_id=photo_id,
                                           format='jpg',
                                           overwrite=True,
                                           invalidate=True,
                                           use_filename=True)

    # If there isn't photo in the folder
    else:

        # Check if the user uploaded any photo
        if trip_photos[0].filename != "":

            # Send uploded photos to the cloud
            for trip_photo in range(len(trip_photos)):
                file = trip_photos[trip_photo]
                category = trip_category.lower().replace(" ", "_")
                folder_name = trip_name.replace(" ", "_").lower()

                photo_id = "%s_%s" % (folder_name, trip_photo)

                folder_path = "users/%s/trips/%s/%s/" % (current_user_id,
                                                         category,
                                                         folder_name)
                cloudinary.uploader.upload(file,
                                           folder=folder_path,
                                           public_id=photo_id,
                                           format='jpg',
                                           overwrite=True,
                                           invalidate=True,
                                           use_filename=True)


class Pagination:
    """
    Handle pagination
    """

    def __init__(self,
                 db,
                 db_field,
                 db_field_data,
                 sort_data,
                 sort_direction,
                 offset,
                 limit):

        self.db = db
        self.db_field = db_field
        self.db_field_data = db_field_data
        self.sort_data = sort_data
        self.sort_direction = sort_direction
        self.offset = offset
        self.limit = limit

    def all_data(self):
        """
        Return all data in db
        """
        db = self.db
        if self.db_field is None or self.db_field_data is None:
            all_data = list(db.find().sort(
                self.sort_data, self.sort_direction))
        else:
            all_data = list(db.find(
                {self.db_field: self.db_field_data}).sort(
                self.sort_data, self.sort_direction))

        return all_data

    def pag_data(self):
        """
        Define the number of data will
        be shown per page
        """

        offset = int(self.offset)
        limit = int(self.limit)
        db = self.db

        if self.db_field is None or self.db_field_data is None:
            data = list(db.find().sort(
                self.sort_data, self.sort_direction).skip(
                offset).limit(limit))
        else:
            data = list(db.find(
                {self.db_field: self.db_field_data}).sort(
                self.sort_data, self.sort_direction).skip(
                offset).limit(limit))

        output = []
        for d in data:
            output.append(d)

        return output

    def num_pages(self):
        """
        return the number of pages
        """

        num_pages = math.ceil(len(self.all_data())/self.limit)

        return num_pages

    def pag_link(self, pag_name, sec_arg, limit, offset, page):
        """
        Return the link for each page
        """

        if sec_arg is None:
            link = '/%s?limit=%s&offset=%s&page=%s' % (pag_name,
                                                       limit,
                                                       offset,
                                                       page)
        else:
            link = '/%s/%s?limit=%s&offset=%s&page=%s' % (pag_name,
                                                          sec_arg,
                                                          limit,
                                                          offset,
                                                          page)

        return link


# View for landpage
@app.route("/")
def landpage():
    current_user_id = session['user']
    current_user = mongo.db.users.find_one(
        {'_id': ObjectId(current_user_id)})
    notifications = current_user['notifications']

    if 'user' not in session:
        return render_template("landpage.html",
                               notifications=notifications)
    else:
        return redirect(url_for('profile'))


# View for Sign Up Page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Check if the username already exists in db
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email")})

        if existing_user:
            flash("User already exists")
            return redirect(url_for("signup"))

        register = {
            "fname": request.form.get("fname").lower(),
            "lname": request.form.get("lname").lower(),
            "email": request.form.get("email"),
            "following": [],
            "followers": [],
            "notifications": [],
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        registered_user = mongo.db.users.find_one(
            {"email": request.form.get("email")})

        # Put the new user into 'session' cookie
        session['user'] = str(registered_user["_id"])
        flash("Registration Successful")

        # Create a folder for the user to store images
        # Create folder and file name
        # for default profile and cover pictures
        user_id = mongo.db.users.find_one(
            {"_id": ObjectId(session["user"])})
        default_profile_pic = 'static/images/default_profile_pic.png'
        default_cover_pic = 'static/images/default_cover_pic.jpg'
        profile_folder_id = "default_profile_pic"
        cover_folder_id = "default_cover_pic"
        profile_folder = "users/%s/profile/" % user_id['_id']
        cover_folder = "users/%s/cover/" % user_id['_id']

        # Create folder in the cloud platform
        cloudinary.uploader.upload(default_profile_pic,
                                   folder=profile_folder,
                                   public_id=profile_folder_id,
                                   format='jpg')
        cloudinary.uploader.upload(default_cover_pic,
                                   folder=cover_folder,
                                   public_id=cover_folder_id,
                                   format='jpg')

        return redirect(url_for("profile"))

    return render_template("signup.html")


# View to execute the login page and form (Read from DB)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Check if the username exists in database
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email")})

        if existing_user:
            # Ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = str(existing_user["_id"])
                flash("Welcome, {}".format(
                    existing_user["fname"].capitalize()))
                return redirect(url_for("profile"))

            else:
                # Invalid password
                flash("Incorrect username and/or password")
                return redirect(url_for("login"))

        else:
            # Username doesn't exist
            flash("Incorrect username and/or password")
            return redirect(url_for("login"))

    return render_template("login.html")


# View to execute the profile
# (Add new trip button, feed to show the trips, followers,
#  following and statistics)
@app.route("/profile", methods=["GET", "POST"])
def profile():

    # Current user
    current_user = mongo.db.users.find_one(
        {'_id': ObjectId(session['user'])})

    # Current user ID
    current_user_id = current_user['_id']

    if request.method == "POST":

        # Catch data from form into variables
        trip_category = request.form.get("trip_category")
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

        # New trip dictionary to insert into database
        new_trip = {
            "user": current_user_id,
            "trip_category": trip_category,
            "trip_name": trip_name,
            "trip_place_name": trip_place_name,
            "trip_country": trip_country,
            "trip_description": trip_description,
            "trip_startdate": trip_startdate,
            "trip_end_date": trip_end_date,
            "trip_likes": [],
            "trip_privacy": trip_privacy
        }

        # Insert new_trip into database
        flash('Trip successfully added')
        mongo.db.trips.insert_one(new_trip)

        # Create trip folder to host trip photos
        if trip_photos[0].filename != "":
            for trip_photo in range(len(trip_photos)):
                file = trip_photos[trip_photo]
                category = trip_category.lower().replace(" ", "_")
                folder_name = trip_name.replace(" ", "_")
                photo_id = "%s_%s" % (folder_name, trip_photo)
                folder_path = "users/%s/trips/%s/%s/" % (current_user_id,
                                                         category,
                                                         folder_name)
                cloudinary.uploader.upload(file,
                                           folder=folder_path,
                                           public_id=photo_id,
                                           format='jpg')
        else:
            category = trip_category.lower().replace(" ", "_").lower()
            folder_name = trip_name.replace(" ", "_").lower()
            folder_path = "users/%s/trips/%s/%s" % (current_user_id,
                                                    category,
                                                    folder_name)
            cloudinary.api.create_folder(folder_path)

    # List of countries
    countries = list(mongo.db.countries.find())

    # Pagination
    db = mongo.db.trips
    db_field = 'user'
    db_field_data = ObjectId(session['user'])
    sort_data = 'trip_startdate'
    sort_direction = -1

    if request.args:
        offset = int(request.args['offset'])
        limit = int(request.args['limit'])
        page = int(request.args['page'])

        profile_pag = Pagination(db,
                                 db_field,
                                 db_field_data,
                                 sort_data,
                                 sort_direction,
                                 offset,
                                 limit)
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
                                 limit)

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

    # Get full name
    first_name = current_user['fname'].capitalize()
    last_name = current_user['lname'].capitalize()
    full_name = "%s %s" % (first_name, last_name)

    # Verify if the user has trips recorded
    user_trips = []
    if len(profile_pag.all_data()):
        for trip in profile_pag.all_data():
            user_trips.append(trip)

    notifications = current_user['notifications']

    return render_template('profile.html',
                           countries=countries,
                           trips=trips_pag,
                           full_name=full_name,
                           current_user_id=current_user_id,
                           user_trips=user_trips,
                           profile_pic=get_profile_pic,
                           cover_pic=get_cover_pic,
                           bg_post_url=get_BGPost_pic,
                           no_files=get_no_pictures,
                           num_pages=num_pages,
                           limit=limit,
                           offset=offset,
                           page=page,
                           prev_pag=prev_pag,
                           next_pag=next_pag,
                           pag_link=profile_pag.pag_link,
                           notifications=notifications)


# Public profile view
@ app.route('/public_profile/<trip_user>')
def public_profile(trip_user):
    user = mongo.db.users.find_one({'_id': ObjectId(trip_user)})

    # Pagination
    db = mongo.db.trips
    db_field = 'user'
    db_field_data = ObjectId(trip_user)
    sort_data = 'trip_startdate'
    sort_direction = -1

    if request.args:
        offset = int(request.args['offset'])
        limit = int(request.args['limit'])
        page = int(request.args['page'])

        pprofile_pag = Pagination(db,
                                  db_field,
                                  db_field_data,
                                  sort_data,
                                  sort_direction,
                                  offset,
                                  limit)
    else:
        offset = 0
        limit = 5
        page = 1

        pprofile_pag = Pagination(db,
                                  db_field,
                                  db_field_data,
                                  sort_data,
                                  sort_direction,
                                  offset,
                                  limit)

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

    # Get full name
    first_name = user['fname'].capitalize()
    last_name = user['lname'].capitalize()
    full_name = "%s %s" % (first_name, last_name)

    # Get notifications for the current user
    current_user_id = session['user']
    current_user = mongo.db.users.find_one(
        {'_id': ObjectId(current_user_id)})
    notifications = current_user['notifications']

    # Public profile user
    user = mongo.db.users.find_one(
        {'_id': ObjectId(trip_user)})
    user_ntf = user['notifications']

    ntf_id = []
    for ntf in range(len(user_ntf)):
        ntf_id.append(user_ntf[ntf]['_id'])

    return render_template('public_profile.html',
                           profile_pic=get_profile_pic,
                           cover_pic=get_cover_pic,
                           bg_post_url=get_BGPost_pic,
                           no_files=get_no_pictures,
                           trips=trips_pag,
                           user=user,
                           full_name=full_name,
                           num_pages=num_pages,
                           limit=limit,
                           offset=offset,
                           page=page,
                           prev_pag=prev_pag,
                           next_pag=next_pag,
                           pag_link=pprofile_pag.pag_link,
                           notifications=notifications,
                           ntf_id=ntf_id)


# Count likes
@ app.route('/likes/<trip_id>', methods=["GET", "POST"])
def likes(trip_id):
    current_user = session['user']
    trip_id = trip_id
    trip = mongo.db.trips.find_one({'_id': ObjectId(trip_id)})
    likes = trip['trip_likes']

    lk = {
        'user': current_user,
    }

    if len(likes) > 0:
        for like in range(len(likes)):
            user = likes[like]['user']
            if user != current_user:
                mongo.db.trips.update({'_id': ObjectId(trip_id)}, {
                    '$push': {
                        'trip_likes': lk
                    }})
                like_icon = "true"
            else:
                mongo.db.trips.update({'_id': ObjectId(trip_id)}, {
                    '$pull': {
                        'trip_likes': lk
                    }})
                like_icon = "false"
    else:
        mongo.db.trips.update({'_id': ObjectId(trip_id)}, {
            '$push': {
                'trip_likes': lk
            }})
        like_icon = "true"

    updated_trip = mongo.db.trips.find_one({'_id': ObjectId(trip_id)})
    updated_likes = updated_trip['trip_likes']
    count_likes = len(updated_likes)

    return jsonify({'result': 'success',
                    'current_user': current_user,
                    'trip_id': trip_id,
                    'like_icon': like_icon,
                    'count_likes': count_likes})


# View to execute the Feed page
@ app.route('/edit_profile', methods=["POST", "GET"])
def edit_profile():
    current_user = mongo.db.users.find_one({'_id': ObjectId(session['user'])})
    current_user_id = current_user['_id']

    if request.method == 'POST':

        # Update profile and cover pictures
        profile_photo = request.files['profile_photo']
        if profile_photo.filename != "":
            update_profile_pic(profile_photo)

        cover_photo = request.files['cover_photo']
        if cover_photo.filename != "":
            update_cover_pic(cover_photo)

        # Data from form
        updated_data = {
            'fname': request.form.get('fname'),
            'lname': request.form.get('lname')
        }

        # Update Name and last name
        mongo.db.users.update({"_id": ObjectId(current_user_id)},
                              {'$set': updated_data},
                              multi=True)
        flash('Profile Updated')
        return redirect(url_for('profile'))

    notifications = current_user['notifications']

    return render_template("edit_profile.html",
                           profile_pic=get_profile_pic,
                           cover_pic=get_cover_pic,
                           current_user=current_user,
                           notifications=notifications)


# View to edit a trip
@ app.route('/edit_trip/<trip_id>', methods=['GET', 'POST'])
def edit_trip(trip_id):
    current_trip = mongo.db.trips.find_one({'_id': ObjectId(trip_id)})
    current_catg = current_trip['trip_category'].lower()
    current_name = current_trip['trip_name'].lower()
    current_user = session['user']
    search_exp = (current_trip['trip_name']).replace(" ", " AND ")
    trip_path = cloudinary.Search().expression(search_exp).execute()
    resources = trip_path['resources']

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

        # Edit trip dictionary to update into database
        edit_trip = {
            "user": current_trip['user'],
            "trip_category": trip_category,
            "trip_name": trip_name,
            "trip_place_name": trip_place_name,
            "trip_country": trip_country,
            "trip_description": trip_description,
            "trip_startdate": trip_startdate,
            "trip_end_date": trip_end_date,
            "trip_privacy": trip_privacy
        }

        # If the user keeps the trip category and trip name
        if trip_category == current_catg and trip_name == current_name:

            # Update trip data in database
            flash('Trip Updated')
            mongo.db.trips.update({"_id": ObjectId(current_trip['_id'])},
                                  {'$set': edit_trip},
                                  multi=True)

            # Send trip photos to folder in the cloud
            update_trip_photos(trip_photos,
                               resources,
                               trip_category,
                               trip_name,
                               current_user)

            return redirect(url_for('profile'))

        # If the user changes the trip category and trip name
        elif trip_category != current_catg or trip_name != current_name:
            # Create new folder with the new trip category and trip name
            category = trip_category.lower().replace(" ", "_").lower()
            folder_name = trip_name.replace(" ", "_").lower()
            folder_path = "users/%s/trips/%s/%s" % (current_trip['user'],
                                                    category,
                                                    folder_name)
            cloudinary.api.create_folder(folder_path)

            # If there is any photo in the old folder
            # Then tranfer these photos to the new folder
            if len(resources) > 0:
                for res in range(len(resources)):
                    public_id = resources[res]['public_id']
                    filename = '%s_%s' % (folder_name,
                                          res)
                    new_folder = '%s/%s' % (folder_path,
                                            filename)
                    cloudinary.uploader.rename(public_id,
                                               new_folder,
                                               overwrite=True,
                                               invalidate=True,
                                               use_filename=True)

            # Delete the old folder
            old_folder = resources[0]['folder']
            cloudinary.api.delete_folder(old_folder)

            # List of all photos in the new folder
            new_resources = trip_folder_resources(trip_name)

            # Send new photos to the new folder
            update_trip_photos(trip_photos,
                               new_resources,
                               trip_category,
                               trip_name,
                               current_user)

            # Update trip data in database
            flash('Trip Updated')
            mongo.db.trips.update({"_id": ObjectId(current_trip['_id'])},
                                  {'$set': edit_trip},
                                  multi=True)
            return redirect(url_for('profile'))

    # List of countries
    countries = list(mongo.db.countries.find())

    current_user_id = session['user']
    current_user = mongo.db.users.find_one(
        {'_id': ObjectId(current_user_id)})
    notifications = current_user['notifications']

    return render_template('edit_trip.html',
                           profile_pic=get_profile_pic,
                           current_user=current_user,
                           current_trip=current_trip,
                           countries=countries,
                           trip_path=trip_path,
                           img_url=img_url,
                           notifications=notifications)


# Delete one image from cloud
@ app.route('/delete_img/<trip_id>/<filename>', methods=["GET", "POST"])
def delete_img(trip_id, filename):
    trip = mongo.db.trips.find_one({'_id': ObjectId(trip_id)})
    trip_user = trip['user']
    trip_catg = trip['trip_category'].replace(" ", "_").lower()
    trip_name = trip['trip_name'].replace(" ", "_").lower()
    public_id = 'users/%s/trips/%s/%s/%s' % (trip_user,
                                             trip_catg,
                                             trip_name,
                                             filename)
    delete_folder = 'users/%s/delete' % trip_user
    cloudinary.uploader.rename(public_id, delete_folder)
    cloudinary.uploader.destroy(delete_folder)

    return jsonify({'result': 'success'})


# View to execute the delete_trip
@ app.route('/delete_trip/<trip_id>')
def delete_trip(trip_id):
    trip = mongo.db.trips.find_one({'_id': ObjectId(trip_id)})
    search_exp = (trip['trip_name']).replace(" ", " AND ")
    trip_path = cloudinary.Search().expression(search_exp).execute()

    # Delete trip pictures and folder from cloud
    if trip_path['total_count'] > 0:
        res = trip_path['resources']
        for img in range(len(res)):
            resources = res[img]
            delete_folder = 'users/%s/delete' % trip['user']

            cloudinary.uploader.rename(resources['public_id'], delete_folder)
            cloudinary.uploader.destroy(delete_folder)

        trip_folder = trip_path['resources'][0]['folder']
        cloudinary.api.delete_folder(trip_folder)
    else:
        trip_user = trip['user']
        trip_catg = trip['trip_category'].replace(" ", "_").lower()
        trip_name = trip['trip_name'].replace(" ", "_").lower()
        trip_folder = 'users/%s/trips/%s/%s' % (trip_user,
                                                trip_catg,
                                                trip_name)
        cloudinary.api.delete_folder(trip_folder)

    # Delete trip from database
    mongo.db.trips.remove({"_id": ObjectId(trip_id)})
    flash("Trip Successfuly Deleted")
    return redirect(request.referrer)


# View to execute the Feed page
@ app.route('/feed', methods=["POST", "GET"])
def feed():
    # Current user
    current_user = mongo.db.users.find_one(
        {'_id': ObjectId(session['user'])})

    # Current user ID
    current_user_id = current_user['_id']

    # Pagination
    db = mongo.db.trips
    db_field = None
    db_field_data = None
    sort_data = '_id'
    sort_direction = -1

    if request.args:
        offset = int(request.args['offset'])
        limit = int(request.args['limit'])
        page = int(request.args['page'])

        feed_pag = Pagination(db,
                              db_field,
                              db_field_data,
                              sort_data,
                              sort_direction,
                              offset,
                              limit)
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
                              limit)

    trips_pag = feed_pag.pag_data()
    num_pages = feed_pag.num_pages()
    prev_pag = feed_pag.pag_link('feed',
                                 None,
                                 limit,
                                 (offset - limit),
                                 (page - 1))
    next_pag = feed_pag.pag_link('feed',
                                 None,
                                 limit,
                                 (offset + limit),
                                 (page + 1))

    notifications = current_user['notifications']

    return render_template("feed.html",
                           current_user_id=current_user_id,
                           trips=trips_pag,
                           bg_post_url=get_BGPost_pic,
                           no_files=get_no_pictures,
                           user_photo=user_post_photo,
                           profile_pic=get_profile_pic,
                           num_pages=num_pages,
                           limit=limit,
                           offset=offset,
                           page=page,
                           prev_pag=prev_pag,
                           next_pag=next_pag,
                           pag_link=feed_pag.pag_link,
                           notifications=notifications)


# View to open the trip post
@app.route('/trip/<trip_id>')
def trip(trip_id):
    trip = mongo.db.trips.find_one({'_id': ObjectId(trip_id)})
    resources = trip_folder_resources(trip['trip_name'])

    num_photos = get_no_pictures(trip['user'], trip['_id'])
    map = map_key

    current_user_id = session['user']
    current_user = mongo.db.users.find_one(
        {'_id': ObjectId(current_user_id)})
    notifications = current_user['notifications']

    return render_template('trip.html',
                           trip=trip,
                           profile_pic=get_profile_pic,
                           resources=resources,
                           img_url=img_url,
                           map=map,
                           num_photos=num_photos,
                           notifications=notifications)


# Notifications
@app.route("/notification/<user_id>", methods=["POST", "GET"])
def notification(user_id):
    current_user_id = session['user']
    current_user = mongo.db.users.find_one(
        {'_id': ObjectId(current_user_id)})
    user = mongo.db.users.find_one(
        {'_id': ObjectId(user_id)})
    ntf_user = user['notifications']

    ntf = {
        '_id': current_user_id,
        'name': current_user['fname'].capitalize()
    }

    if len(ntf_user) > 0:
        for notif in ntf_user:
            # Add notification
            if session['user'] != notif['_id']:
                mongo.db.users.update({'_id': ObjectId(user_id)}, {
                    '$push': {
                        'notifications': ntf
                    }})

            # Remove notification
            else:
                mongo.db.users.update({'_id': ObjectId(user_id)}, {
                    '$pull': {
                        'notifications': ntf
                    }})
    else:
        # Add notification
        mongo.db.users.update({'_id': ObjectId(user_id)}, {
            '$push': {
                'notifications': ntf
            }})

    return jsonify({
        'result': 'success',
        'user_id': user_id,
        'current_user': current_user_id
    })


# Follow request
@app.route("/follow_request/<user_id>")
def follow_request(user_id):
    return jsonify({
        'result': 'success',
        'user': user_id
    })


# View to logout the user (Clear the session cookie)
@app.route("/logout")
def logout():
    # Remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


# Define host and port for the app
# Tell the app how and where to run
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
