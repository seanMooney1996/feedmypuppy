from pubnub.pnconfiguration import PNConfiguration
from pubnub.models.consumer.v3.channel import Channel
from pubnub.pubnub import PubNub, SubscribeCallback
from pubnub.exceptions import PubNubException
from fmp_pi.pubnub.listeners import PubNubListener
import os
import threading
import time
from dotenv import load_dotenv


class PubNubClient:
    def __init__(self, handlers = {},cipher=None):
        load_dotenv()
        self.pubnub = None
        self.cipher = cipher
        self.handlers = handlers
        self.initiate_pubnub()


    def initiate_pubnub(self):
        try:
            print("Cipher key in pubnub config ",self.cipher)
            pnconfig = PNConfiguration()
            pnconfig.publish_key = os.getenv("PUBLISH_PUBNUB_KEY")
            pnconfig.subscribe_key = os.getenv("SUBSCRIBE_PUBNUB_KEY")
            pnconfig.secret_key = os.getenv("SECRET_PUBNUB_KEY")
            pnconfig.ssl = True
            pnconfig.cipher_key = self.cipher
            pnconfig.uuid = os.getenv("PUBNUB_USERID")
            self.pubnub = PubNub(pnconfig)
            self.pubnub.add_listener(PubNubListener(self.handlers))
            print("PubNub connected successfully")
        except Exception as e:
            print(f"PubNub connection failed: {e}")
    
    
    def publish_message(self, channel, message):
        try:
            print(f"Publish message on {channel}. Message : {message}")
            envelope = self.pubnub.publish().channel(channel).message(message).sync()
            if envelope.status.is_error():
                print(f"Error publishing message on {channel}")
            else:
                print("Message published")
        except PubNubException as e:
            print("Error publishing:", e)
            return True


    def subscribe_to_channel(self, channel):
        # Subscribe to a specified channel
        self.pubnub.subscribe().channels(channel).execute()
        
        
    def initiate_token_refresh(self,token):
        while True:
            parsed_token = self.pubnub.parse_token(token)
            ttl_minutes = int(parsed_token.get('ttl'))
            print("Parsed token TTL ->", ttl_minutes)
            sleep_time = (ttl_minutes * 60) - 30
            time.sleep(sleep_time)
            print("Setting new token")
            token = self.request_auth_token()
            self.pubnub.set_token(token)
            #test the token
        
        
