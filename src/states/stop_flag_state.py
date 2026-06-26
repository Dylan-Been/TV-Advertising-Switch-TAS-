stop_flag = False # True or False 

def stop_recording():
    global stop_flag
    stop_flag = not stop_flag
    print("stop_flag:", stop_flag)
    
def get_stop_flag():
    global stop_flag
    return stop_flag