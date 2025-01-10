from datetime import datetime
from functools import wraps
import os, time, threading
import pathlib
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for
import requests
from mongodb.mongo_client import MongoDBClient
from pubnub_flask.pubnub_client import PubNubClient
from pubnub_flask.handlers import Channel_Handler
from cryptography.fernet import Fernet
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow 
from pip._vendor import cachecontrol
import google.auth.transport.requests
app = Flask(__name__)


load_dotenv()

PUBNUB_CIPHER_KEY = Fernet.generate_key().decode()

SECRET_API_KEY = os.getenv('SECRET_API_KEY')
GOOGLE_CLIENT_ID =(os.getenv("GOOGLE_CLIENT_ID"))
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "google_auth_secrets.json")
app.secret_key = os.getenv("SECRET_FLASK_KEY")

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes = ["https://www.googleapis.com/auth/userinfo.profile","https://www.googleapis.com/auth/userinfo.email","openid"],
    redirect_uri = "http://127.0.0.1:5000/login/authorized"
)

mongodb = MongoDBClient()
channel_handler = Channel_Handler(mongodb)
PUBNUB_CIPHER_KEY = Fernet.generate_key().decode()
print("Cipher key in flask server",PUBNUB_CIPHER_KEY)
pubnub = PubNubClient({"dispenser_event":channel_handler.handle_dispense_event},
                      PUBNUB_CIPHER_KEY)
channel_handler.add_pubnub_client(pubnub)
pubnub.subscribe_to_channel("dispenser_event")


# handle sending dispense events from the server
#get current settings when server spins up
current_settings = mongodb.get_dispenser_settings()


# a condition to stop/start dispense loop
stop_dispense_loop = False
thread_lock = threading.Lock()

# call anytime client updates the settings,stop dispense loop, start thread again with updated settings 
def update_current_settings():
    global current_settings, stop_dispense_loop, dispenser_thread, thread_lock
    #check is there is any threads running and wait for it to stop before starting new dispense loop
    with thread_lock:  
        if dispenser_thread is not None and dispenser_thread.is_alive():
            stop_dispense_loop = True
            dispenser_thread.join()  
        stop_dispense_loop = False
        current_settings = mongodb.get_dispenser_settings()
        dispenser_thread = threading.Thread(target=send_dispense_loop)
        dispenser_thread.start()


def update_current_settings_thread():
    update_thread = threading.Thread(target=update_current_settings)
    update_thread.start()


#loop to send message to dispenser with amount to feed
def send_dispense_loop():
    global stop_dispense_loop,current_settings
    print("start of dispense loop")
    feedTimings = []
    if (current_settings['mode']=='automatic'):
        feedTimings = current_settings['automatic_settings']['feedTimes']
    else:
        feedTimings = current_settings['manual_settings']
    print("FEED TIMINGS ->",feedTimings)
    #map each timing to it's dispense amount
    timing_dict = {item['time']: item['amount'] for item in feedTimings}
    while stop_dispense_loop == False:
        current_time = datetime.now().strftime("%H:%M")
        if current_time in timing_dict:
            pubnub.publish_message("dispense_listener",timing_dict[current_time])
            print('Dispense amount -> ',timing_dict[current_time])
        sleep_until_next_minute()


#use to check time every minute for dispense
def sleep_until_next_minute():
    now = datetime.now()
    seconds_to_next_minute = 60 - now.second
    time.sleep(seconds_to_next_minute)


# run dispense loop on a thread
dispenser_thread = threading.Thread(target=send_dispense_loop)
dispenser_thread.start()           
       


@app.template_filter('datetimeformat')
def format_datetime(value):
    value = datetime.fromisoformat(value)
    return value.strftime('%b %d, %Y %I:%M %p') 


def login_is_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "logged_in" in session:
            if session["logged_in"] != True:
                return redirect("/login")
        return function(*args, **kwargs) 
    return wrapper


@app.route('/')
@login_is_required
def index():
    try:
        dispense_data = list(mongodb.get_feed_data())
        return render_template('index.html',dispense_data = dispense_data)
    except Exception as e:
        return f"An error occurred: {e}"
    

@app.route('/settings')
@login_is_required
def settings():
    try:
        dispenser_settings = mongodb.get_dispenser_settings()
        print(dispenser_settings)
        return render_template('settings.html',dispenser_settings = dispenser_settings)
    except Exception as e:
        return f"An error occurred: {e}"
 
 
@app.route('/change_settings_mode', methods=['POST'])
def change_settings_mode():
    if "google_id" in session:
        data = request.get_json()
        print("setting mode->",data)
        result = mongodb.update_settings_mode(data['mode'])
        update_current_settings_thread()
        print(result)
        return jsonify({"Succes": True})
    else:
        return jsonify({"error": "Unauthorized"}), 401   
 
    
@app.route('/delete_manual_setting', methods=['POST'])
def delete_manual_setting():
    if "google_id" in session:
        data = request.get_json()
        print("Data in delete manual setting ",data)
        result = mongodb.delete_manual_setting(data['index'])
        update_current_settings_thread()
        print(result)
        return jsonify({"Succes": True})
    else:
        return jsonify({"error": "Unauthorized"}), 401


@app.route('/add_manual_setting', methods=['POST'])
def add_manual_setting():
    if "google_id" in session:
        data = request.get_json()
        print("Data in add manual setting ",data)
        result = mongodb.add_manual_setting(data['time'],data['amount'])
        update_current_settings_thread()
        print(result)
        return jsonify({"Succes": True})
    else:
        return jsonify({"error": "Unauthorized"}), 401
    

@app.route('/set_automatic_setting', methods=['POST'])
def set_automatic_setting():
    if "google_id" in session:
        data = request.get_json()
        result = mongodb.set_automatic_setting(data)
        print(result)
        return jsonify({"Succes": True})
    else:
        return jsonify({"error": "Unauthorized"}), 401

    
@app.route('/login')
def login():
    try:
        return render_template('login.html')
    except Exception as e:
        return f"An error occurred: {e}"
    
    
@app.route("/logout")
def logout():
    try:
        session.clear()
        return redirect("/login")
    except Exception as e:
        print("Error Logging out ",e)
        return "Error"
    
    
@app.route('/unauthorized')
def unauthorized():
    try:
        return "Unauthorized"
    except Exception as e:
        return f"An error occurred: {e}"    


@app.route("/google_login")
def google_login():
    try:
        authorization_url, state = flow.authorization_url()
        session["state"] = state
        return redirect(authorization_url)
    except Exception as e:
        print("Error with google login ",e)
        return "Error "


@app.route('/login/authorized')
def authorized():
    flow.fetch_token(authorization_response=request.url)
    if not session["state"] == request.args["state"]:
        abort(500)
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session = cached_session)
    
    id_info = id_token.verify_oauth2_token(
        id_token = credentials._id_token,
        request = token_request,
        audience = GOOGLE_CLIENT_ID
    )
    session["google_id"] = id_info.get("sub")
    print(session["google_id"])
    session["name"] = id_info.get("name")
    session['email'] = id_info.get('email')
    user = mongodb.get_user_by_email(session['email'])
    print(session['email'])
    print(session["name"])
    if user is None:
        session.clear()
        # return "Invalid User"
        session["logged_in"] = False
        return redirect("/unauthorized")
    session["logged_in"] = True
    return redirect("/")


@app.route('/get_cipher_key', methods=['POST'])
def get_cipher_key():
    # #Check if the user has been authenticated
    # print("Attempting cipher request")
    # if "google_id" in session:  
    #     print("Cipher key sent to client",PUBNUB_CIPHER_KEY)
    #     return jsonify({"cipher_key": PUBNUB_CIPHER_KEY})
    #  # Or check if the pi has the secret pi key   
    if request.headers.get("Authorization") == SECRET_API_KEY:
         return jsonify({"cipher_key": PUBNUB_CIPHER_KEY})
    else:   
        return jsonify({"error": "Unauthorized"})


@app.route("/get_pubnub_token", methods=['POST'])
def get_pubnub_token():
    # #Check if the user has been authenticated
    # if "google_id" in session: 
    #     token_result = pubnub.generate_token_client()
    #     if token_result:
    #         return jsonify({"token": token_result})
    # # Or check if the pi has the secret pi key
    print("secretapikey  ", SECRET_API_KEY)
    if request.headers.get("Authorization") == SECRET_API_KEY:
        print("Gnerating token and sending to pi")
        token_result = pubnub.generate_token_pi()
        return jsonify({"token": token_result})
    else:
        print("Unauthorized for token")
        return jsonify({"error": "Unauthorized"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)