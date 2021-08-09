import os
if os.path.exists('env.py'):
    import env


# config settings and environmental variables
class Config:
    MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
    MONGO_URI = os.environ.get("MONGO_URI")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    MAP_KEY = os.environ.get("MAP_KEY")
