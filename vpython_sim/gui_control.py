from vpython.no_notebook import stop_server
import keyboard
from sys import exit
import os
import signal

# https://github.com/BruceSherwood/vpython-jupyter/issues/36

def monitor_terminate():
    if keyboard.is_pressed('q'):    
        print("Exit function triggered. Sending the kill signal.")
        # stop_server() # this didn't work for me, hangs on this function usually
        # print("Server stopped.")
        os.kill(os.getpid(), signal.SIGINT)
        exit()

def monitor_pause():
    if keyboard.is_pressed('p'):
        print("Pause triggered.")
        while True:
            if keyboard.is_pressed('r'):
                print("Resuming")
                return
            if keyboard.is_pressed('q'):
                print("Exit function triggered. Sending the kill signal.")
                os.kill(os.getpid(), signal.SIGINT)
                exit()
