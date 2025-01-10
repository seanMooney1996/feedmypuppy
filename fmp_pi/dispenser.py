from load_cell import Load_Cell
from hatch import Hatch

hatch = Hatch()
load_cell = Load_Cell()


def main():
    input_weight = float(input("Enter weight in grams: "))
    dispense_until_weight_or_full(input_weight)
             

def dispense_until_weight_or_full(target_weight):
    previous_weight = load_cell.get_weight_in_grams()
    total_dispensed = 0
    has_reached_weight = False
    stuck_count = 0

    while (not load_cell.is_full_bowl()) and (not has_reached_weight):
        if stuck_count == 3:
            print("Food dispenser is stuck or is empty.")
            break
        
        hatch.drop_food_sequence()
        new_weight = load_cell.get_weight_in_grams()
        if not has_weight_changed(previous_weight, load_cell.get_weight_in_grams()) :
            stuck_count += 1 
        else:
            total_dispensed += new_weight - previous_weight
        
        if load_cell.is_within_tolerance(total_dispensed,target_weight) :
            has_reached_weight = True
        previous_weight = new_weight  
        
    if load_cell.is_full_bowl(): 
            print("bowl is full")
    elif has_reached_weight:
            print("weight requirement met") 



def has_weight_changed(previous_weight,weight_now):
    if load_cell.is_within_tolerance(previous_weight,weight_now):
        return False
    return True


if __name__ == "__main__":
    main()
