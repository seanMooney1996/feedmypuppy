from pubnub_pi.pubnub_client import PubNubClient
from pubnub_pi.handlers import Channel_Handler
from datetime import datetime
import os
import threading



def main():
    print("start test")
    channel_handler = Channel_Handler()
    pubnub = PubNubClient({"return_test_chan":channel_handler.handle_return_test_chan})
    pubnub.subscribe_to_channel("return_test_chan")
    pubnub.publish_message("test_chan","From pi test")
    
    
    
    
if __name__ == "__main__":
    main()