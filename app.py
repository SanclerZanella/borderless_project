import os
from flask import (Flask, flash,
                   render_template, redirect,
                   request, session, url_for)
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
  cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.environ.get('CLOUDINARY_API_KEY'), 
  api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
  secure = True
)

# View for landpage
@app.route("/")
def landpage():
    if 'user' not in session:
        return render_template("landpage.html")
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
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # Put the new user into 'session' cookie
        session['user'] = existing_user["fname"].capitalize()
        flash("Registration Successful")
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
                session["user"] = existing_user["fname"].capitalize()
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
        {'fname': session['user'].lower()})

    # Current user ID
    current_user_id = ObjectId(current_user['_id'])

    if request.method == "POST":

        # Catch data from form into variables
        trip_category = request.form.get("trip_category")
        trip_name = request.form.get("trip_name")
        trip_place_name = request.form.get("trip_place_name")
        trip_country = request.form.get("trip_country")
        trip_description = request.form.get("trip_description")
        trip_startdate = dt.datetime.strptime(
            request.form.get("trip_startdate"), '%Y-%m-%d')
        trip_end_date = dt.datetime.strptime(
            request.form.get("trip_end_date"), '%Y-%m-%d')
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
            "trip_privacy": trip_privacy
        }

        # Insert new_trip into database
        mongo.db.trips.insert_one(new_trip)

    # List of countries
    countries = list(mongo.db.countries.find())

    # List of trips
    trips = list(mongo.db.trips.find())

    return render_template('profile.html', countries=countries, trips=trips,
                           current_user_id=current_user_id)


# View to execute the Feed page
@app.route('/feed', methods=["POST", "GET"])
def feed():
    if request.method == "POST":
        uploaded_files = request.files.getlist("file")

        if len(uploaded_files) != 0:
            for uploaded_file in range(len(uploaded_files)):
                photo_trip = uploaded_files[uploaded_file]
                trip_name = 'Cancun'
                file_id = uploaded_file
                filename = "trip_%s_%s" % (trip_name, file_id)
                cloudinary.uploader.upload(photo_trip,
                                           public_id = "users/trips/%s" % filename)

    imgSample = cloudinary.CloudinaryImage("sample.jpg").url
    return render_template("feed.html", imgSample=imgSample)


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
