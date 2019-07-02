from modules.HeatClient import *
import argparse, time

__author__ = "Tamas Szabo"
__email__ = "tamas.e.szabo@ericsson.com"

def check_stack(stack_name, progress_state, finish_state, timeout):
    '''
    '''
    time_spent = 0
    h = HeatClient()
    current_status = progress_state
    state_changed = False
    
    while current_status == progress_state and time_spent < timeout:
        
        try:
            current_status =  h.get_stack(stack_name)["stack"]["stack_status"]
        except ValueError, e:
            #if operation was delete (i.e. finish state is not applicable) and the stack is gone, we're done!
            if str(e).endswith('could not be found') and finish_state=='N/A':
                print("Successful after %s seconds" % str(time_spent))
                return
            #if it's a different error, or the operation was not delete, raise the received exception
            else:
                raise e
        
        if current_status != progress_state:
            state_changed = True
            break
        print("Current status is %s.\nWaiting 10 second before checking" % current_status)
        time.sleep(10)
        time_spent += 10
        
    if state_changed and current_status == finish_state:
        print("Successful after %s seconds" % str(time_spent))
        return
    elif state_changed and current_status != finish_state:
        print("Failed after %s seconds" % str(time_spent))
        exit(1)
    else:
        print("Timeout after %s seconds" % str(time_spent))
        exti(1)
    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--stack", help="name of the Heat stack", type=str, required=True)
    parser.add_argument("-o", "--operation", help="operation that's happening with the stack", type=str, choices=['create','delete'], required=True)
    parser.add_argument("-t", "--timeout", help="max time to wait before givingup. optional and defaults to 1200 seconds (20 minutes)", type=str, required=False, default="1200")
    args = parser.parse_args()
    
    if args.operation == "create":
        check_stack(args.stack, 'CREATE_IN_PROGRESS', 'CREATE_COMPLETE', args.timeout)
    elif args.operation == "delete":
        check_stack(args.stack, 'DELETE_IN_PROGRESS', 'N/A', args.timeout)  #when delete is done, stack disappears -> finish state is not applicable 