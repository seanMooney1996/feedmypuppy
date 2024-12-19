import os
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from mongodb.mongo_client import MongoDBClient
from pubnub_flask.pubnub_client import PubNubClient
from pubnub_flask.handlers import Channel_Handler
from cryptography.fernet import Fernet
app = Flask(__name__)


load_dotenv()

PUBNUB_CIPHER_KEY = Fernet.generate_key().decode()
SECRET_API_KEY = os.getenv('SECRET_API_KEY')


mongodb = MongoDBClient()
channel_handler = Channel_Handler(mongodb)
PUBNUB_CIPHER_KEY = Fernet.generate_key().decode()
print("Cipher key in flask server",PUBNUB_CIPHER_KEY)
pubnub = PubNubClient({"test_chan":channel_handler.handle_test_chan},
                      PUBNUB_CIPHER_KEY)
channel_handler.add_pubnub_client(pubnub)
pubnub.subscribe_to_channel("test_chan")


@app.route('/')
def index():
    try:
        users = mongodb.get_users()
        return render_template('index.html',users = users)
    except Exception as e:
        return f"An error occurred: {e}"


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