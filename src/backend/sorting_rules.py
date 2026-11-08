#this file should just simply categorizes what bin it should go into, very obvious but needs to be done 

#names are subject to changed 

#should be the current sorting rules for the items
def get_bin(confidence, category):

    #low confidence case will default to a garbage
    if (confidence < 0.20):
        return "garbage_bin"

    
    if (category == "food_scraps"):
        return "compost_bin"
    elif (category == "recyclable_container"):
        return "recycling_bin"
    elif (category == "paper"):
        return "paper_bin"
    elif (category == "garbage"):
        return "garbage_bin"


BIN_TO_LED = {
    "compost_bin": 0,     
    "recycling_bin": 1,  
    "paper_bin": 2,       
    "garbage_bin": 3,     
}

#using the dictionary 
def get_led(bin_name):
    return BIN_TO_LED.get(bin_name, 3)