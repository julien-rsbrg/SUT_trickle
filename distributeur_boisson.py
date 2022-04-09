import random

def simulate_non_determinism():
    return random.choice([True, False])
        
class SystemSignatureViolation(Exception): pass

def can_loop(io_controller):
    ev_name = io_controller.get_input()
    if(ev_name == "SODA"):
        g = simulate_non_determinism()
        if g:
            print("CAN")
            return False
        else:
            print("UNAV")
            return True
    elif(ev_name == "CANCEL"):
        return False
    else:
        raise SystemSignatureViolation()

def coin_loop(io_controller):
    ev_name = io_controller.get_input()
    if(ev_name == "COIN"):
        g = simulate_non_determinism()
        if g:
            print("GOOD")
            while(g):
                g=can_loop(io_controller)
        else:
            print("BAD")
    else:
        raise SystemSignatureViolation()
        
def start_machine(io_controller):
    while(True):
        coin_loop(io_controller)
        
import sys,os
import datetime

class IOController(object):
    def __init__(self):
        self.terminal = sys.stdout
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.log = open("boisson_%s.log" % current_time , "a")

    def write_output(self, message):
        if not message.endswith(os.linesep):
            message += os.linesep
        self.terminal.write(message)
        self.log.write(message)
        
    def get_input(self):
        got = input()
        if not got.endswith(os.linesep):
            self.log.write(got + os.linesep)
        else:
            self.log.write(got)
        return got
    
if __name__ == '__main__':
    io_controller = IOController()
    try:
        start_machine(io_controller)
    except SystemSignatureViolation:
        io_controller.write_output("ABORT")
    
    
    
    
    

