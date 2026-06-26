import subprocess
#restarting the entrire pc 
def restart_program():
    subprocess.run(["shutdown", "/r", "/t", "0"])