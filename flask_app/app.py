from functools import wraps
import os
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

print(f"GOOGLE_CLIENT_ID: {GOOGLE_CLIENT_ID}")
print(f"Client Secrets File ID: {flow.client_config['client_id']}")

mongodb = MongoDBClient()
channel_handler = Channel_Handler(mongodb)
PUBNUB_CIPHER_KEY = Fernet.generate_key().decode()
print("Cipher key in flask server",PUBNUB_CIPHER_KEY)
pubnub = PubNubClient({"test_chan":channel_handler.handle_test_chan},
                      PUBNUB_CIPHER_KEY)
channel_handler.add_pubnub_client(pubnub)
pubnub.subscribe_to_channel("test_chan")


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
        users = mongodb.get_users()
        return render_template('index.html',users = users)
    except Exception as e:
        return f"An error occurred: {e}"
    
    
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