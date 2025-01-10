
from pubnub_pi.pubnub_client import PubNubClient

class Channel_Handler:
    def add_pubnub_client(self, client : PubNubClient):
        self.pubnub_client = client
           
           
    def handle_return_test_chan(self,data):
        print("Handling message in return test chan ",data)
        
    
    def handle_return_test_chan(self,data):
        print("Handling message in return test chan ",data)
        
    
    def handle_dispense_trigger(self,data):
        print("dispense amount ",data)
        