from flask import Flask, render_template
from mongodb.mongo_client import MongoDBClient
from pubnub.pubnub_client import PubNubClient
from pubnub.handlers import Channel_Handler
from cryptography.fernet import Fernet
app = Flask(__name__)



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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)