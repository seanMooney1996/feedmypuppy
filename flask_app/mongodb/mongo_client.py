from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId
import gridfs
import base64
from datetime import datetime
from functools import wraps


class MongoDBClient:
    def __init__(self):
        load_dotenv()
        self.client = None
        self.db = None
        self.user_collection = None
        self.connect()


    def connect(self):
        try:
            # Get MongoDB credentials from environment 
            MONGO_PASSWORD = os.getenv('MONGODB_PASS')
            self.USER = os.getenv('MONGODB_USER')
            uri = f"mongodb+srv://{self.USER}:{MONGO_PASSWORD}@feedmypuppy.t47bg.mongodb.net/?retryWrites=true&w=majority&appName=feedmypuppy"
            self.client = MongoClient(uri, server_api=ServerApi('1'))
            self.db = self.client['feedmypuppy']
            self.user_collection = self.db['user']
            self.event_collection = self.db['event']
            self.settings_collection = self.db['settings']
            self.log_collection = self.db['logs']
            self.fs = gridfs.GridFS(self.db)
            print("MongoDB connected successfully")
        except Exception as e:
            print(f"MongoDB connection failed: {e}")


    def mongo_log(action, collection):
        def decorator(function):
            @wraps(function)
            def wrapper(self, *args, **kwargs):
                try:
                    result = function(self, *args, **kwargs)
                    self.log_db_operation(action=action, collection=collection, status="SUCCESS", returned=str(result), user=self.USER)
                    return result
                except Exception as e:
                    self.log_db_operation(action=action, collection=collection, status="FAILURE", returned=None, user=self.USER)
                    print(f"Error logging MongoDB action: {e}")
            return wrapper
        return decorator


    def log_db_operation(self,action, collection,status, returned="",user="",):
        log_entry = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "action": action,
        "status":status,
        "collection": collection,
        "returned": returned,
        "user":user
        }
        self.log_collection.insert_one(log_entry)


    @mongo_log(action="FIND", collection="user")
    def get_users(self):
        if self.user_collection is not None:
            try:
                users = list(self.user_collection.find({}, {"_id": 0}))
                return users
            except Exception as e:
                print(f"Error retrieving users: {e}")
                return []     
        
        
    @mongo_log(action="FIND_ONE", collection="user")
    def get_user_by_email(self,email):
        try:
            user = self.user_collection.find_one({"email":email})
            print("Retrieved user ",user)
            return user
        except Exception as e:
            print(f"Failed to user by email from MongoDB: {e}")
            return None
 
    @mongo_log(action="FIND", collection="event")
    def get_feed_data(self):
        try:
            events = self.event_collection.find({},{"_id": 0})
            print("Retreived all feed data",events)
            return events
        except Exception as e:
            print(f"Failed to get feed data : {e}")
            return None     
        

    @mongo_log(action="FIND", collection="settings")
    def get_dispenser_settings(self):
        try:
            settings = self.settings_collection.find_one({},{"_id": 0})
            print("Retreived settings ",settings)
            return settings
        except Exception as e:
            print(f"Failed to get settings in mongo function : {e}")
            return None   
        
    
    @mongo_log(action="UPDATE_ONE", collection="settings")
    def delete_manual_setting(self,index):
        try:
            settings = self.get_dispenser_settings()
            settings["manual_settings"].pop(index)
            result = self.db.settings.update_one({"settings_id": settings["settings_id"]},
            {"$set": {"manual_settings": settings["manual_settings"]}})
        except Exception as e:
            print(f"Failed to delete manual setting in mongo function : {e}")
            return None 
        
        
    @mongo_log(action="UPDATE_ONE", collection="settings")
    def add_manual_setting(self,time,amount):
        try:
            settings = self.get_dispenser_settings()
            newRow = {'time':time,'amount':amount}
            settings["manual_settings"].append(newRow)
            result = self.db.settings.update_one(
                {"settings_id": settings["settings_id"]},
                {"$set": {"manual_settings": settings["manual_settings"]}})
            return result
        except Exception as e:
            print(f"Failed to add manual setting in mongo function : {e}")
            return None 
        

    mongo_log(action="UPDATE_ONE", collection="settings")
    def update_settings_mode(self,settings_mode):
        try:
            settings = self.get_dispenser_settings()
            result = self.db.settings.update_one(
                {"settings_id": settings["settings_id"]},
                {"$set": {"mode": settings_mode}})
            return result
        except Exception as e:
            print(f"Failed to update settings mode in mongo function : {e}")
            return None 
        

    def set_automatic_setting(self,automatic_settings):
        try:
            print("settings ",automatic_settings)
            settings = self.get_dispenser_settings()
            result = self.db.settings.update_one(
                {"settings_id": settings["settings_id"]},
                {"$set": {"automatic_settings": automatic_settings}})
            return result
        except Exception as e:
            print(f"Failed to add automatic setting in mongo function : {e}")
            return None 
