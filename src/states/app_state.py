app_state = 'ziggo' #ziggo or youtube 

def switch_currentstate(new_state):
    global app_state
    app_state = new_state   
    
def get_currentstate():
    global app_state
    return app_state