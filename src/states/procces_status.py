status = 'Clear' # Busy or Clear

def switch_proccesstate(new_state):
    global status
    if new_state == True: 
        status = "Busy"
    else:
        status = "Clear"   
    
def get_proccesstate():
    global status
    return status