from flask import (session, redirect, url_for)
import math
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import cloudinary
import cloudinary.uploader
import cloudinary.api
from app.app import mongo
from app.config import Config


# Configure Cloudinary API
cloudinary.config(
    cloud_name=Config.CLOUD_NAME,
    api_key=Config.API_KEY,
    api_secret=Config.API_SECRET,
    secure=True
)


# DB collections
users_collections = mongo.db.users
trips_collection = mongo.db.trips


# Helper Classes
class User:
    """
    Handle all users functionality

    Attributes:
        *fname: A string indicating the user's first name;
        *lname: A string indicating the user's last name;
        *email: A string indicating the user's email;
        *password: A string indicating the user's password

    Methods:
        *register: Handle user registration creating user document
                  in data base;
        *cloud_folder: Create a user's fold in cloud platform
                      when the user is registered,
                      to store the images;
        *login: Handle the user login, putting the user into a session;
        *get_full_name: Get user's fullname concatenating the fname(first name)
                        and the lname(last name);
        *get_profile_pic: Get the profile pic of any user from the cloud
                          platform;
        *get_cover_pic: Get the cover pic of any user from the cloud platform;
        *update_profile_pic: Update the profile pic of any user in the cloud;
        *update_cover_pic: Update the cover pic of any user in the cloud;
        *update_name: Update the name of any user in database;
        *notifications: Handle user's notifications creation and deletion;
        *follow_request: Handle follow request add in database
                         or removing from database;
        *remove_follower: Remove follower from followers array in database and
                          remove current user from following array
                          in the other user database;
        *logout: Handle user logout, removing his session
    """

    def __init__(self,
                 fname,
                 lname,
                 email,
                 password):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.password = password

    def register_user(self):
        """
        Handle user registration in
        database
        """

        register = {
            "fname": self.fname.lower(),
            "lname": self.lname.lower(),
            "email": self.email,
            "followers": [],
            "following": [],
            "notifications": [],
            "password": generate_password_hash(self.password)
        }
        users_collections.insert_one(register)

    def cloud_folder(self, id):
        """
        Create a folder for the users to store the images
        and set the default cover and profile picture
        """
        pic_path = 'app/static/images/profile/default_profile_pic.png'
        default_profile_pic = pic_path
        default_cover_pic = 'app/static/images/profile/default_cover_pic.jpg'
        profile_folder_id = "default_profile_pic"
        cover_folder_id = "default_cover_pic"
        profile_folder = "users/%s/profile/" % id
        cover_folder = "users/%s/cover/" % id
        delete_folder = "users/%s/delete" % id
        trips_folder = "users/%s/trips" % id

        # Create folder in the cloud platform

        # Profile folder
        cloudinary.uploader.upload(default_profile_pic,
                                   folder=profile_folder,
                                   public_id=profile_folder_id,
                                   format='jpg')

        # Cover Folder
        cloudinary.uploader.upload(default_cover_pic,
                                   folder=cover_folder,
                                   public_id=cover_folder_id,
                                   format='jpg')

        # Delete Folder
        cloudinary.api.create_folder(delete_folder)

        # Trips Folder
        cloudinary.api.create_folder(trips_folder)

    def login(self):
        """
        Handle the user login
        """

        # Check if the username exists in database
        user = users_collections.find_one(
            {"email": self.email})

        # Ensure hashed password matches user input
        pw = check_password_hash(user["password"], self.password)

        if user:
            if pw:
                existing_user = True
                password = True
            else:
                existing_user = True
                password = False
        else:
            existing_user = False
            password = False

        return existing_user, password, user

    def get_full_name(self, id):
        """
        Get user's full name
        """

        user = users_collections.find_one({'_id': ObjectId(id)})
        first_name = user['fname'].capitalize()
        last_name = user['lname'].capitalize()
        full_name = "%s %s" % (first_name, last_name)

        return full_name

    def get_profile_pic(self, user_id):
        """
        Get user's profile picture url
        """

        profile_folder_id = "default_profile_pic"
        profile_folder = "users/%s/profile/" % user_id
        profile_pic_path = "%s/%s" % (profile_folder, profile_folder_id)
        profile_pic_url = cloudinary.CloudinaryImage(profile_pic_path).url

        return profile_pic_url

    def get_cover_pic(self, user_id):
        """
        Get user's cover picture url
        """

        cover_folder_id = "default_cover_pic"
        cover_folder = "users/%s/cover/" % user_id
        cover_pic_path = "%s/%s" % (cover_folder, cover_folder_id)
        cover_pic_url = cloudinary.CloudinaryImage(cover_pic_path).url

        return cover_pic_url

    def update_profile_pic(self, profile_photo):
        """
        Update user's profile picture
        """

        default_profile_pic = profile_photo
        profile_folder_id = "default_profile_pic"
        profile_folder = "users/%s/profile/" % session["user"]

        cloudinary.uploader.upload(default_profile_pic,
                                   folder=profile_folder,
                                   public_id=profile_folder_id,
                                   format='jpg',
                                   overwrite=True,
                                   invalidate=True,
                                   use_filename=True)

    def update_cover_pic(self, cover_photo):
        """
        Update user's cover pictures
        """

        default_cover_pic = cover_photo
        cover_folder_id = "default_cover_pic"
        cover_folder = "users/%s/cover/" % session["user"]

        cloudinary.uploader.upload(default_cover_pic,
                                   folder=cover_folder,
                                   public_id=cover_folder_id,
                                   format='jpg',
                                   overwrite=True,
                                   invalidate=True,
                                   use_filename=True)

    def update_name(self):
        """
        Update user's name in DB
        """

        # Data from form
        updated_data = {
            'fname': self.fname,
            'lname': self.lname
        }

        # Update Name and last name
        users_collections.update({"_id": ObjectId(session['user'])},
                                 {'$set': updated_data},
                                 multi=True)

    def notification(self, current_user, user, ntf_user, user_id):
        """
        Handle user's notifications
        """

        # Notifications content
        # (Current user id and first name)
        ntf = {
            '_id': session['user'],
            'name': current_user['fname'].capitalize()
        }

        # Verify if the user has any notification
        if len(ntf_user) > 0:

            # Verify if any of user's friend request
            # notification is from current_user
            for notif in ntf_user:
                # Add notification
                if session['user'] != notif['_id']:
                    users_collections.update({'_id': ObjectId(user_id)}, {
                        '$push': {
                            'notifications': ntf
                        }})

                else:

                    # Remove notification
                    users_collections.update({'_id': ObjectId(user_id)}, {
                        '$pull': {
                            'notifications': ntf
                        }})
        else:
            # Add notification
            users_collections.update({'_id': ObjectId(user_id)}, {
                '$push': {
                    'notifications': ntf
                }})

    def follow_request(self, current_user, rqt_current_user, user, user_id):
        """
        Handle follow request
        """

        # Following
        flwg = session['user']
        # Follower
        flwr = user_id

        # Notifications content
        # (Any user id and first name)
        ntf = {
            '_id': user_id,
            'name': user['fname'].capitalize()
        }

        # Check if user is already a current user's follower
        if len(rqt_current_user) > 0:

            if user_id not in rqt_current_user:
                """
                If user is not a current user's follower
                the user will be added to current user's
                followers list and the current user will
                be added to user's following list
                """

                users_collections.update({'_id': ObjectId(user_id)}, {
                    '$push': {
                        'following': flwg
                    }})

                users_collections.update({'_id': ObjectId(session['user'])}, {
                    '$push': {
                        'followers': flwr
                    }})

                users_collections.update({'_id': ObjectId(session['user'])}, {
                    '$pull': {
                        'notifications': ntf
                    }})
            else:
                """
                If user is a current user's follower
                the user will be removed from current user's
                followers list and the current user will
                be removed from user's following list
                """

                users_collections.update({'_id': ObjectId(user_id)}, {
                    '$pull': {
                        'followers': flwg
                    }})

                users_collections.update({'_id': ObjectId(session['user'])}, {
                    '$pull': {
                        'following': flwr
                    }})
        else:
            """
            If the current_user has not followers, then the
            user will be added to current user's followers list
            and the current user will be added to user's following
            list
            """

            users_collections.update({'_id': ObjectId(user_id)}, {
                '$push': {
                    'following': flwg
                }})

            users_collections.update({'_id': ObjectId(session['user'])}, {
                '$push': {
                    'followers': flwr
                }})

            users_collections.update({'_id': ObjectId(session['user'])}, {
                '$pull': {
                    'notifications': ntf
                }})

        # Update followers count
        updated_user = users_collections.find_one(
            {'_id': ObjectId(session['user'])})
        updated_following = updated_user['following']
        count_following = len(updated_following)

        return count_following

    def remove_follower(self, id):
        """
        Remove follower from followers array in database and
        remove current user from following array
        in the other user database
        """

        # Following
        fwl = session['user']
        # Followers
        flwr = id

        # Remove follower from followers array in database
        users_collections.update({'_id': ObjectId(session['user'])}, {
            '$pull': {
                'followers': flwr
            }})

        # Remove current user from following array
        # in the other user database
        users_collections.update({'_id': ObjectId(id)}, {
            '$pull': {
                'following': fwl
            }})

        # Update followers count
        updated_user = users_collections.find_one(
            {'_id': ObjectId(session['user'])})
        updated_followers = updated_user['followers']
        count_followers = len(updated_followers)

        return count_followers

    def logout(self):
        """
        Handle user logout
        """

        session.pop("user")


class Trip:
    """
    Handle all trips functionality

    Attributes:
        *user: An ObjectId indicating the user's document ID in DB;
        *user_name: A string indicating the user's first name;
        *category: A string indicating the trip's category, which are
                   Travel, Vacation and Short Trip;
        *trip_name: A string indicating the trip's name;
        *place_name: A string indicating the trip's place name;
        *country: A string indicating the trip's country;
        *description: A long string indicating the trip's description;
        *start_date: A date type indicating the trip's start date;
        *end_date: A date type indicating the trip's end date;
        *privacy: A string indicating the trip's privacy, which are
                  Public, Private and Friends;

    Methods:
        *countries: Return a list of all countries to be used when add
                    a new trip or edit a trip;
        *new_trip: Insert a new trip in database;
        *cloud_folder: Create a folder in the cloud platform for the
                       trip when its created;
        *get_BGPost_pic: Return trip post background image url;
        *get_no_pictures: Get the number os image files of a certain
                          trip folder;
        *user_post_photo: Return trip post author image url;
        *edit_trip: Update trip in databe and cloud platform;
        *delete_img: Delete an image from cloud platform;
        *delete_tip: Delete a trip from database and cloud platform;
        *like: Insert or delete a like from database;
        *img_url: Get url of an image from cloud platform;
        *folder_resources: Get all info and resources of a trip folder
                           in cloud platform;
        *statistics: Handle statistics amounts;
        *update_trip_photos: Update the trip photos in the cloud
    """

    def __init__(self,
                 user,
                 user_name,
                 category,
                 trip_name,
                 place_name,
                 country,
                 description,
                 start_date,
                 end_date,
                 privacy):
        self.user = user
        self.user_name = user_name
        self.category = category
        self.trip_name = trip_name
        self.place_name = place_name
        self.country = country
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.privacy = privacy

    def countries(self):
        """
        List of countries
        """

        countries = ["Afghanistan",
                     "land Islands",
                     "Albania",
                     "Algeria",
                     "American Samoa",
                     "AndorrA",
                     "Angola",
                     "Anguilla",
                     "Antarctica",
                     "Antigua and Barbuda",
                     "Argentina",
                     "Armenia",
                     "Aruba",
                     "Australia",
                     "Austria",
                     "Azerbaijan",
                     "Bahamas",
                     "Bahrain",
                     "Bangladesh",
                     "Barbados",
                     "Belarus",
                     "Belgium",
                     "Belize",
                     "Benin",
                     "Bermuda",
                     "Bhutan",
                     "Bolivia",
                     "Bosnia and Herzegovina",
                     "Botswana",
                     "Bouvet Island",
                     "Brazil",
                     "British Indian Ocean Territory",
                     "Brunei Darussalam",
                     "Bulgaria",
                     "Burkina Faso",
                     "Burundi",
                     "Cambodia",
                     "Cameroon",
                     "Canada",
                     "Cape Verde",
                     "Cayman Islands",
                     "Central African Republic",
                     "Chad",
                     "Chile",
                     "China",
                     "Christmas Island",
                     "Cocos (Keeling) Islands",
                     "Colombia",
                     "Comoros",
                     "Congo",
                     "Congo, The Democratic Republic of the",
                     "Cook Islands",
                     "Costa Rica",
                     "Cote D'Ivoire",
                     "Croatia",
                     "Cuba",
                     "Cyprus",
                     "Czech Republic",
                     "Denmark",
                     "Djibouti",
                     "Dominica",
                     "Dominican Republic",
                     "Ecuador",
                     "Egypt",
                     "El Salvador",
                     "Equatorial Guinea",
                     "Eritrea",
                     "Estonia",
                     "Ethiopia",
                     "Falkland Islands (Malvinas)",
                     "Faroe Islands",
                     "Fiji",
                     "Finland",
                     "France",
                     "French Guiana",
                     "French Polynesia",
                     "French Southern Territories",
                     "Gabon",
                     "Gambia",
                     "Georgia",
                     "Germany",
                     "Ghana",
                     "Gibraltar",
                     "Greece",
                     "Greenland",
                     "Grenada",
                     "Guadeloupe",
                     "Guam",
                     "Guatemala",
                     "Guernsey",
                     "Guinea",
                     "Guinea-Bissau",
                     "Guyana",
                     "Haiti",
                     "Heard Island and Mcdonald Islands",
                     "Holy See (Vatican City State)",
                     "Honduras",
                     "Hong Kong",
                     "Hungary",
                     "Iceland",
                     "India",
                     "Indonesia",
                     "Iran, Islamic Republic Of",
                     "Iraq",
                     "Ireland",
                     "Isle of Man",
                     "Israel",
                     "Italy",
                     "Jamaica",
                     "Japan",
                     "Jersey",
                     "Jordan",
                     "Kazakhstan",
                     "Kenya",
                     "Kiribati",
                     "Korea, Democratic People'S Republic of",
                     "Korea, Republic of",
                     "Kuwait",
                     "Kyrgyzstan",
                     "Lao People'S Democratic Republic",
                     "Latvia",
                     "Lebanon",
                     "Lesotho",
                     "Liberia",
                     "Libyan Arab Jamahiriya",
                     "Liechtenstein",
                     "Lithuania",
                     "Luxembourg",
                     "Macao",
                     "Macedonia, The Former Yugoslav Republic of",
                     "Madagascar",
                     "Malawi",
                     "Malaysia",
                     "Maldives",
                     "Mali",
                     "Malta",
                     "Marshall Islands",
                     "Martinique",
                     "Mauritania",
                     "Mauritius",
                     "Mayotte",
                     "Mexico",
                     "Micronesia, Federated States of",
                     "Moldova, Republic of",
                     "Monaco",
                     "Mongolia",
                     "Montenegro",
                     "Montserrat",
                     "Morocco",
                     "Mozambique",
                     "Myanmar",
                     "Namibia",
                     "Nauru",
                     "Nepal",
                     "Netherlands",
                     "Netherlands Antilles",
                     "New Caledonia",
                     "New Zealand",
                     "Nicaragua",
                     "Niger",
                     "Nigeria",
                     "Niue",
                     "Norfolk Island",
                     "Northern Mariana Islands",
                     "Norway",
                     "Oman",
                     "Pakistan",
                     "Palau",
                     "Palestinian Territory, Occupied",
                     "Panama",
                     "Papua New Guinea",
                     "Paraguay",
                     "Peru",
                     "Philippines",
                     "Pitcairn",
                     "Poland",
                     "Portugal",
                     "Puerto Rico",
                     "Qatar",
                     "Reunion",
                     "Romania",
                     "Russian Federation",
                     "RWANDA",
                     "Saint Helena",
                     "Saint Kitts and Nevis",
                     "Saint Lucia",
                     "Saint Pierre and Miquelon",
                     "Saint Vincent and the Grenadines",
                     "Samoa",
                     "San Marino",
                     "Sao Tome and Principe",
                     "Saudi Arabia",
                     "Senegal",
                     "Serbia",
                     "Seychelles",
                     "Sierra Leone",
                     "Singapore",
                     "Slovakia",
                     "Slovenia",
                     "Solomon Islands",
                     "Somalia",
                     "South Africa",
                     "South Georgia and the South Sandwich Islands",
                     "Spain",
                     "Sri Lanka",
                     "Sudan",
                     "Suriname",
                     "Svalbard and Jan Mayen",
                     "Swaziland",
                     "Sweden",
                     "Switzerland",
                     "Syrian Arab Republic",
                     "Taiwan",
                     "Tajikistan",
                     "Tanzania, United Republic of",
                     "Thailand",
                     "Timor-Leste",
                     "Togo",
                     "Tokelau",
                     "Tonga",
                     "Trinidad and Tobago",
                     "Tunisia",
                     "Turkey",
                     "Turkmenistan",
                     "Turks and Caicos Islands",
                     "Tuvalu",
                     "Uganda",
                     "Ukraine",
                     "United Arab Emirates",
                     "United Kingdom",
                     "United States",
                     "United States Minor Outlying Islands",
                     "Uruguay",
                     "Uzbekistan",
                     "Vanuatu",
                     "Venezuela",
                     "Viet Nam",
                     "Virgin Islands, British",
                     "Virgin Islands, U.S.",
                     "Wallis and Futuna",
                     "Western Sahara",
                     "Yemen",
                     "Zambia",
                     "Zimbabwe"]
        return countries

    def new_trip(self):
        """
        Insert New trip into database
        """

        # New trip dictionary to insert into database
        new_trip = {
            "user": self.user,
            "user_name": self.user_name,
            "trip_category": self.category,
            "trip_name": self.trip_name,
            "trip_place_name": self.place_name,
            "trip_country": self.country,
            "trip_description": self.description,
            "trip_startdate": self.start_date,
            "trip_end_date": self.end_date,
            "trip_likes": [],
            "trip_privacy": self.privacy
        }

        # Insert new_trip into database
        trips_collection.insert_one(new_trip)

    def cloud_folder(self, photo_files):
        """
        Create a folder in cloud platform for the new trip
        to store the trip pictures
        """

        if photo_files[0].filename is not None:
            if photo_files[0].filename != "":
                for trip_photo in range(len(photo_files)):
                    file = photo_files[trip_photo]
                    category = self.category.lower().replace(" ", "_")
                    trip_name = self.trip_name.replace(" ", "_").lower()
                    photo_id = "%s_%s" % (trip_name, trip_photo)
                    folder_path = "users/%s/trips/%s/%s/" % (session['user'],
                                                             category,
                                                             trip_name)
                    cloudinary.uploader.upload(file,
                                               folder=folder_path,
                                               public_id=photo_id,
                                               format='jpg')
            else:
                category = self.category.lower().replace(" ", "_").lower()
                trip_name = self.trip_name.replace(" ", "_").lower()
                folder_path = "users/%s/trips/%s/%s" % (session['user'],
                                                        category,
                                                        trip_name)
                cloudinary.api.create_folder(folder_path)
        else:
            category = self.category.lower().replace(" ", "_").lower()
            trip_name = self.trip_name.replace(" ", "_").lower()
            folder_path = "users/%s/trips/%s/%s" % (session['user'],
                                                    category,
                                                    trip_name)
            cloudinary.api.create_folder(folder_path)

    def get_BGPost_pic(self, user_id, trip_id):
        """
        Get the url to post background picture
        """

        post = trips_collection.find_one(
            {'_id': ObjectId(trip_id)})
        num_pic = self.get_no_pictures(user_id, trip_id)

        if num_pic > 0:
            category = (post['trip_category']).replace(" ", "_").lower()
            trip_name = (post['trip_name']).replace(" ", "_").lower()
            search_exp = 'folder=users/%s/trips/%s/%s' % (post['user'],
                                                          category,
                                                          trip_name)
            trip_path = cloudinary.Search().expression(search_exp).execute()
            res = trip_path['resources'][-1]
            first_pic = res['public_id']
            post_BGpic_url = cloudinary.CloudinaryImage(
                '%s.jpg' % first_pic).url
            return post_BGpic_url
        else:
            local_img = '../static/images/trip_post/default_post_cover.jpg'
            return local_img

    def get_no_pictures(self, trip_user, trip_id):
        """
        Get number of pictures in a folder
        """

        user = users_collections.find_one(
            {'_id': ObjectId(trip_user)})
        current_user_id = user['_id']
        post = trips_collection.find_one(
            {'_id': trip_id})

        if current_user_id == post['user']:
            category = (post['trip_category']).replace(" ", "_").lower()
            trip_name = (post['trip_name']).replace(" ", "_").lower()
            search_exp = 'folder=users/%s/trips/%s/%s' % (trip_user,
                                                          category,
                                                          trip_name)
            search_cloud = cloudinary.Search().expression(search_exp).execute()
            no_files = search_cloud['total_count']
            return no_files

    def user_post_photo(self, user_id):
        """
        Get the profile photo of the post author
        """

        user = users_collections.find_one(
            {'_id': ObjectId(user_id)})
        user_id = user['_id']
        profile_folder_id = "default_profile_pic"
        profile_folder = "users/%s/profile/" % user_id
        profile_pic_path = "%s/%s" % (profile_folder, profile_folder_id)
        profile_pic_url = cloudinary.CloudinaryImage(profile_pic_path).url

        return profile_pic_url

    def edit_trip(self,
                  current_catg,
                  current_name,
                  resources,
                  current_trip,
                  trip_photos,
                  ids):
        """
        Handle edit trip functionality
        """

        # Edit trip dictionary to update into database
        edit_trip = {
            "user": self.user,
            "trip_category": self.category,
            "trip_name": self.trip_name,
            "trip_place_name": self.place_name,
            "trip_country": self.country,
            "trip_description": self.description,
            "trip_startdate": self.start_date,
            "trip_end_date": self.end_date,
            "trip_privacy": self.privacy
        }

        # If the user keeps the trip category and trip name
        if self.category == current_catg and self.trip_name == current_name:

            # Update trip data in database
            trips_collection.update({"_id": ObjectId(current_trip['_id'])},
                                    {'$set': edit_trip},
                                    multi=True)

            # Send trip photos to folder in the cloud
            self.update_trip_photos(trip_photos,
                                    resources,
                                    self.category,
                                    self.trip_name,
                                    session['user'],
                                    ids)

            return redirect(url_for('profile.profile'))

        # If the user changes the trip category and trip name
        elif self.category != current_catg or self.trip_name != current_name:

            # Create new folder with the new trip category and trip name
            category = self.category.lower().replace(" ", "_").lower()
            folder_name = self.trip_name.replace(" ", "_").lower()
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
            # old_folder = resources[0]['folder']
            old_catg = current_catg.replace(" ", "_")
            old_folder = "users/%s/trips/%s" % (self.user,
                                                old_catg)
            old_folder_id = current_name.replace(" ", "_")
            old_folder = "%s/%s" % (old_folder, old_folder_id)
            cloudinary.api.delete_folder(old_folder)

            # List of all photos in the new folder
            new_resources = self.folder_resources(current_trip['_id'])

            # Send new photos to the new folder
            self.update_trip_photos(trip_photos,
                                    new_resources,
                                    self.category,
                                    self.trip_name,
                                    session['user'],
                                    ids)

            # Update trip data in database
            trips_collection.update({"_id": ObjectId(current_trip['_id'])},
                                    {'$set': edit_trip},
                                    multi=True)

    def delete_img(self, trip_id, filename):
        """
        Delete one image from cloud platform
        """

        trip = trips_collection.find_one({'_id': ObjectId(trip_id)})
        trip_user = trip['user']
        trip_catg = trip['trip_category'].replace(" ", "_").lower()
        trip_name = trip['trip_name'].replace(" ", "_").lower()
        public_id = 'users/%s/trips/%s/%s/%s' % (trip_user,
                                                 trip_catg,
                                                 trip_name,
                                                 filename)
        delete_folder = 'users/%s/delete/deleted_img' % trip_user
        cloudinary.uploader.rename(public_id, delete_folder)
        cloudinary.uploader.destroy(delete_folder)

    def delete_trip(self, trip_id):
        """
        View to execute the delete_trip
        """

        trip = trips_collection.find_one({'_id': ObjectId(trip_id)})
        category = (trip['trip_category']).replace(" ", "_").lower()
        trip_name = (trip['trip_name']).replace(" ", "_").lower()
        search_exp = 'folder=users/%s/trips/%s/%s' % (trip['user'],
                                                      category,
                                                      trip_name)
        trip_path = cloudinary.Search().expression(search_exp).execute()

        # Delete trip pictures and folder from cloud
        if trip_path['total_count'] > 0:
            res = trip_path['resources']
            for img in range(len(res)):
                resources = res[img]

                # Delete folder
                delete_folder = 'users/%s/delete/deleted_img' % trip['user']

                cloudinary.uploader.rename(resources['public_id'],
                                           delete_folder)
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
        trips_collection.remove({"_id": ObjectId(trip_id)})

    def like(self, user, id, trip, likes):
        """
        Handle the likes counting
        """

        lk = {
            'user': user,
        }

        if len(likes) > 0:
            for like in range(len(likes)):
                user = likes[like]['user']
                if user != user:
                    trips_collection.update({'_id': ObjectId(id)}, {
                        '$push': {
                            'trip_likes': lk
                        }})
                    like_icon = "true"
                else:
                    trips_collection.update({'_id': ObjectId(id)}, {
                        '$pull': {
                            'trip_likes': lk
                        }})
                    like_icon = "false"
        else:
            trips_collection.update({'_id': ObjectId(id)}, {
                '$push': {
                    'trip_likes': lk
                }})
            like_icon = "true"

        updated_trip = trips_collection.find_one({'_id': ObjectId(id)})
        updated_likes = updated_trip['trip_likes']
        count_likes = len(updated_likes)

        return like_icon, count_likes

    def img_url(self, folder, filename):
        """
        Get image url from cloud
        """
        pic_url = cloudinary.CloudinaryImage('%s/%s' % (folder,
                                                        filename)).url
        return pic_url

    def folder_resources(self, trip_id):
        """
        Provide a list of all images in a trip folder in the cloud
        """
        trip = trips_collection.find_one({'_id': ObjectId(trip_id)})
        category = (trip['trip_category']).replace(" ", "_").lower()
        trip_name = (trip['trip_name']).replace(" ", "_").lower()
        search_exp = 'folder=users/%s/trips/%s/%s' % (trip['user'],
                                                      category,
                                                      trip_name)
        trip_path = cloudinary.Search().expression(search_exp).execute()
        resources = trip_path['resources']

        return resources

    def statistics(self, id):
        """
        Handle statistcs amounts
        """

        trips = trips_collection.find({
            'user': ObjectId(id)})

        # Countries set
        countries_visited = set()

        # Places set
        places_visited = set()

        # Total days traveled
        total_days = []

        # Total photos
        total_photos = []

        for trip in trips:

            # Add countries to countries_visited set
            country = trip['trip_country']
            countries_visited.add(country)

            # Add places to places_visited set
            place = trip['trip_place_name']
            places_visited.add(place)

            # Add amount of time of each trip to
            # total_days list
            start_date = trip['trip_startdate']
            end_date = trip['trip_end_date']
            delta_time = (end_date - start_date).days
            total_days.append(delta_time)

            # Add amount of photos in each trip to
            # total_photos list
            category = (trip['trip_category']).replace(" ", "_").lower()
            trip_name = (trip['trip_name']).replace(" ", "_").lower()
            search_exp = 'folder=users/%s/trips/%s/%s' % (trip['user'],
                                                          category,
                                                          trip_name)
            trip_path = cloudinary.Search().expression(search_exp).execute()
            res = trip_path['total_count']
            total_photos.append(res)

        # Number of visited countries
        num_countries = len(countries_visited)

        # Number of visited places
        num_places = len(places_visited)

        # Sum of total days traveled
        sum_days = sum(total_days)

        # Longest day traveling
        if total_days:
            long_day = max(total_days)
        else:
            long_day = 0

        # Sum of photos
        if total_photos:
            sum_photos = sum(total_photos)
        else:
            sum_photos = 0

        output = (num_countries, num_places,
                  sum_days, long_day, sum_photos)

        return output

    def update_trip_photos(self, trip_photos,
                           resources,
                           trip_category,
                           trip_name,
                           current_user_id,
                           ids):
        """
        Update trip photos in the cloud
        """

        # Check if there is any photo in the trip folder at the cloud
        if len(resources) > 0:

            # Check if the user uploaded any photo
            if trip_photos[0].filename != "":

                # Send uploded photos to the cloud
                for trip_photo in range(len(trip_photos)):
                    file = trip_photos[trip_photo]
                    category = trip_category.lower().replace(" ", "_").lower()
                    folder_name = trip_name.replace(" ", "_").lower()

                    id = 0
                    while True:
                        if id in ids:
                            id += 1
                        else:
                            ids.append(id)
                            break

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

                    id = 0
                    while True:
                        if id in ids:
                            id += 1
                        else:
                            ids.append(id)
                            break

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


class Pagination:
    """
    Handle pagination

    Attributes:
        *db: A string indicating the database path;
        *db_field: A string indicating the database field;
        *db_field_data: A string indicating the database field data
                        which will be used as query parameter;
        *sort_data: A string indicating the sort parameter;
        *sort_direction: A integer indicating the sort direction;
        *offset: A integer indicating the number of data will be skipped;
        *limit: A integer indicating the number of data shown per each page;
        *query: A string indicating a query to be searched

    Methods:
        *all_data: Fetch all data from a specific database of a
                   specific query;
        *pag_data: Fetch the number of data per each page, defined by
                   the offset, limit and query;
        *num_pages: Define the number of pages;
        *pag_link: Define the links for the previous and next pages to
                   show diferent results in each page
    """

    def __init__(self,
                 db,
                 db_field,
                 db_field_data,
                 sort_data,
                 sort_direction,
                 offset,
                 limit,
                 query):

        self.db = db
        self.db_field = db_field
        self.db_field_data = db_field_data
        self.sort_data = sort_data
        self.sort_direction = sort_direction
        self.offset = offset
        self.limit = limit
        self.query = query

    def all_data(self):
        """
        Return all data in db
        """
        db = self.db
        query = self.query

        if query is None:
            if self.db_field is None or self.db_field_data is None:
                all_data = list(db.find().sort(
                    self.sort_data, self.sort_direction))
            else:
                all_data = list(db.find(
                    {self.db_field: self.db_field_data}).sort(
                    self.sort_data, self.sort_direction))
        else:
            all_data = list(db.find({"$text": {"$search": query}}))

        return all_data

    def pag_data(self):
        """
        Define the number of data will
        be shown per page
        """

        offset = int(self.offset)
        limit = int(self.limit)
        db = self.db
        query = self.query

        if query is None:
            if self.db_field is None or self.db_field_data is None:
                data = list(db.find().sort(
                    self.sort_data, self.sort_direction).skip(
                    offset).limit(limit))
            else:
                data = list(db.find(
                    {self.db_field: self.db_field_data}).sort(
                    self.sort_data, self.sort_direction).skip(
                    offset).limit(limit))
        else:
            data = list(db.find({
                '$and': [
                    {self.db_field: self.db_field_data},
                    {"$text": {"$search": query}}
                ]}).sort(
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

        query = self.query

        if query is None:
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
        else:
            if sec_arg is None:
                link = '/%s?query=%s&limit=%s&offset=%s&page=%s' % (pag_name,
                                                                    query,
                                                                    limit,
                                                                    offset,
                                                                    page)
            else:
                link = '/%s/%s?query=%s&limit=%s&offset=%s&page=%s' % (
                    pag_name,
                    sec_arg,
                    query,
                    limit,
                    offset,
                    page)

        return link
