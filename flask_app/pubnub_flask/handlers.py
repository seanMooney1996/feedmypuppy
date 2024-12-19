from mongodb.mongo_client import MongoDBClient
from pubnub_flask.pubnub_client import PubNubClient

class Channel_Handler:
    def __init__(self, mongodb_client: MongoDBClient):
        self.mongodb_client = mongodb_client


    def add_pubnub_client(self, client : PubNubClient):
        self.pubnub_client = client
           
           
    def handle_test_chan(self,data):
        print(f"Handling scan data channel: {data}") 
        self.pubnub_client.publish_message("return_test_chan","Return message")
        