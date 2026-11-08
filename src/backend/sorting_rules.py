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
    "compost_bin": 0,     # leftmost: green (food scraps)
    "recycling_bin": 1,   # second: recyclable containers
    "paper_bin": 2,       # third: paper
    "garbage_bin": 3,     # fourth: garbage
}
