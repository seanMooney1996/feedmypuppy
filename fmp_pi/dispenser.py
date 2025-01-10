from load_cell import Load_Cell
from hatch import Hatch
from datetime import datetime
from pubnub_pi.pubnub_client import PubNubClient
from pubnub_pi.handlers import Channel_Handler
import time, threading

hatch = Hatch()
load_cell = Load_Cell()

def get_average_weight():
    weights = []
    for _ in range(3):
        weight = load_cell.get_weight_in_grams() 
        weights.append(weight)
        
    # must remove outliers because of noise
    weights.sort()
    q1 = weights[len(weights) // 4] 
    q3 = weights[(len(weights) * 3) // 4] 
    iqr = q3 - q1
    filtered_weights = [w for w in weights if q1 - 1.5 * iqr <= w <= q3 + 1.5 * iqr]
    if not filtered_weights:
        filtered_weights = weights
    average_weight = sum(filtered_weights) / len(filtered_weights)
    return max(0, average_weight) 


def get_final_weight():
    weights = [get_average_weight() for _ in range(3)]
    return sum(weights) / len(weights)


#to help track stats to post event statistics at each hour
initial_hourly_weight = get_final_weight()
total_dispensed_tracker = 0
total_not_dispensed = 0
stuck_or_dispenser_empty = False
dispense_in_progress = False

def dispense_until_weight_or_full(target_weight):
    global total_dispensed_tracker,total_not_dispensed, stuck_or_dispenser_empty,dispense_in_progress
    dispense_in_progress = True
    print("Target weight to dispense ",target_weight)
    previous_weight = get_average_weight()
    total_dispensed = 0
    has_reached_weight = False
    stuck_count = 0

    while (not load_cell.is_full_bowl()) and (not has_reached_weight):
        if stuck_count == 3:
            print("Food dispenser is stuck or is empty.")
            stuck_or_dispenser_empty = True
            break
        
        hatch.drop_food_sequence()
        time.sleep(0.5)
        new_weight = get_average_weight()
        if not has_weight_changed(previous_weight, new_weight) :
            stuck_count += 1 
        else:
            total_dispensed += new_weight - previous_weight
            stuck_count = 0
            
        if total_dispensed >= target_weight :
            has_reached_weight = True
        previous_weight = new_weight  
        
    total_dispensed_tracker += total_dispensed
    total_not_dispensed += max(0, target_weight - total_dispensed)
    if load_cell.is_full_bowl(): 
        total_not_dispensed += max(0, target_weight - total_dispensed)
        print("bowl is full")
    elif has_reached_weight:
        print("weight requirement met") 
    dispense_in_progress= False
     
            
channel_handler = Channel_Handler()     
pubnub = PubNubClient({"dispense_listener":dispense_until_weight_or_full},)  
channel_handler.add_pubnub_client(pubnub)
pubnub.subscribe_to_channel("dispense_listener")


def post_stats():
    global total_dispensed_tracker,total_not_dispensed,stuck_or_dispenser_empty, initial_hourly_weight
    final_hour_weight = get_final_weight()
    print("initial weight ", initial_hourly_weight)
    print("final weight" ,final_hour_weight)
    total_eaten = (initial_hourly_weight + total_dispensed_tracker) - final_hour_weight
    total_eaten = round(total_eaten, 1)
    print("Total eaten within hour -> ",total_eaten)
    print("Dispenser empty/ full ",stuck_or_dispenser_empty)
    print("Dispensed amount ",total_dispensed_tracker)
    now_utc = datetime.utcnow()
    timestamp = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    print("timestamp -> ",timestamp)
    if total_eaten < 2.5:
        total_eaten = 0
    event = {'timestamp':timestamp,'dispensed_grams': round(total_dispensed_tracker,1),
             'eaten_grams':total_eaten,'dispenser_status':stuck_or_dispenser_empty,
             'total_not_dispensed': round(total_not_dispensed,1)}
    #only send event if there was a dispense, food eaten or dispenser could not dispense 
    if total_dispensed_tracker > 0 or total_not_dispensed > 0 or total_eaten >= 2.5 or stuck_or_dispenser_empty:
        pubnub.publish_message("dispenser_event",event)
    #reset global tracker variables
    total_dispensed_tracker = 0
    total_not_dispensed = 0
    stuck_or_dispenser_empty = False
    initial_hourly_weight = final_hour_weight


def send_event_loop():
    while True:
        print("Start of wait")
        wait_until_next_minute(2)
        #to provent interference with dispense operation
        while dispense_in_progress == True:
            time.sleep(10)
        print("Sending stats")
        post_stats()


def wait_until_next_minute(wait_minutes):
    for i in range(wait_minutes):
        now = datetime.now()
        seconds_to_next_minute = 60 - now.second  
        time.sleep(seconds_to_next_minute)



def main():
    while True:
        user_input = input("Enter 'stats' to test stats post, 'dispense' to dispense: ")
        if user_input == "stats":
            post_stats()
        elif user_input == "dispense":
            weight_input = float(input("Input dispense weight in grams: "))
            dispense_until_weight_or_full(weight_input)


def has_weight_changed(previous_weight,weight_now):
    if load_cell.is_within_tolerance(previous_weight,weight_now):
        return False
    return True


if __name__ == "__main__":
    dispenser_thread = threading.Thread(target=send_event_loop)
    dispenser_thread.start()  
    main()
