import time
import sys
import os
import keyboard
from datetime import datetime
import win32api, win32con
from etee import EteeController

def console_move (y, x):
    print("\033[%d;%dH" % (y, x))

def console_cls():
    os.system('cls' if os.name=='nt' else 'clear')

def printProgressBar (iteration, total, suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'|{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    #if iteration == total: 
    #    print()

def process_controller(dev):
    loc = [etee.get_data(dev, "trackpad_x"), etee.get_data(dev, "trackpad_y")]
    pressure = [etee.get_data(dev, "trackpad_pull"), etee.get_data(dev, "trackpad_force"),
                etee.get_data(dev, "trackpad_touched"), etee.get_data(dev, "trackpad_clicked")]
    finger_data1 = [etee.get_data(dev, "index_pull"), etee.get_data(dev, "index_force"),
                    etee.get_data(dev, "index_touched"), etee.get_data(dev, "index_clicked")]
    finger_data2 = [etee.get_data(dev, "middle_pull"), etee.get_data(dev, "middle_force"),
                    etee.get_data(dev, "middle_touched"), etee.get_data(dev, "middle_clicked")]
    return loc, pressure, finger_data1, finger_data2

if __name__ == "__main__":
    # Initialise the etee driver and find dongle
    etee = EteeController()
    num_dongles_available = etee.get_number_available_etee_ports()
    if num_dongles_available > 0:
        etee.connect()     # Attempt connection to etee dongle
        time.sleep(1)
        etee.start_data()  # Attempt to send a command to etee controllers to start data stream
        etee.run()         # Start data loop
    else:
        print("No dongle found. Please, insert an etee dongle and re-run the application.")
        sys.exit("Exiting application...")

    controller_selected = "right"
    finger_selected = "index"
    print("Your selected controller hand: ", controller_selected)

    last_mouse_state_left = False
    last_mouse_state_right = False

    # If dongle is connected, print index values
    while True:
        # If 'Esc' key is pressed while printing data, stop controller data stream, data loop and exit application
        if keyboard.is_pressed('Esc'):
            print("\n'Esc' key was pressed. Exiting application...")

            etee.stop_data()  # Stop controller data stream
            print("Controller data stream stopped.")
            etee.stop()  # Stop data loop
            print("Data loop stopped.")

            time.sleep(0.05)
            sys.exit(0)  # Exit driver

        current_time = datetime.now().strftime("%H:%M:%S.%f")
        num_dongles_available = etee.get_number_available_etee_ports()

        if num_dongles_available <= 0:
            print("---")
            print(current_time, "Dongle disconnected. Please, re-insert the dongle and re-run the application.")

            etee.stop_data()  # Stop controller data stream
            print("Controller data stream stopped.")
            etee.stop()  # Stop data loop
            print("Data loop stopped.")

            time.sleep(0.05)
            sys.exit("Exiting application...")

        # Data processing
        selected_loc, selected_pressure, finger_data1, finger_data2 = process_controller(controller_selected)
        if selected_loc[0] == None or finger_data1[0] == None or finger_data2[0] == None:
            print("---")
            print(current_time, f"The {controller_selected} etee controller was not detected. Please reconnect controller.")
            etee.start_data()   # If a controller has reconnected with the dongle, it will start etee controller data stream
            time.sleep(0.05)
        else:
            console_cls()
            console_move(0,0)
            print(f"Controller: {controller_selected}")
            print(f"Finger: {finger_selected}")
            print()
            print(f">>>>> TRACKPAD <<<<<")
            print(f"X     ", end = "")
            printProgressBar(selected_loc[0], 252, printEnd="\n")
            print(f"Y     ", end = "")
            printProgressBar(selected_loc[1], 252, printEnd="\n")
            print(f"Pull  ", end = "")
            printProgressBar(selected_pressure[0], 126, printEnd="\n")
            print(f"Force ", end = "")
            printProgressBar(selected_pressure[1], 126, printEnd="\n")
            print(f"| Touch    | Press    |")
            print(f"{'|          |██████████|' if selected_pressure[3] else '|██████████|          |' if selected_pressure[2] else '|          |          |'}")
            print()
            print(f">>>>> FINGER INDEX <<<<<")
            print(f"Pull  ", end = "")
            printProgressBar(finger_data1[0], 126, printEnd="\n")
            print(f"Force ", end = "")
            printProgressBar(finger_data1[1], 126, printEnd="\n")
            print(f"| Touch    | Press    |")
            print(f"{'|          |██████████|' if finger_data1[3] else '|██████████|          |' if finger_data1[2] else '|          |          |'}")
            print()
            print(f">>>>> FINGER MIDDLE <<<<<")
            print(f"Pull  ", end = "")
            printProgressBar(finger_data2[0], 126, printEnd="\n")
            print(f"Force ", end = "")
            printProgressBar(finger_data2[1], 126, printEnd="\n")
            print(f"| Touch    | Press    |")
            print(f"{'|          |██████████|' if finger_data2[3] else '|██████████|          |' if finger_data2[2] else '|          |          |'}")
            print()
            speed_multiplier = 0.2
            pos_x = selected_loc[0] - 126
            pos_y = -(selected_loc[1] - 126)
            pos_pressure = selected_pressure[0] / 126
            pos_move = selected_pressure[2]
            rel_pos_x = pos_x * pos_pressure * speed_multiplier
            rel_pos_y = pos_y * pos_pressure * speed_multiplier
            click_left = finger_data1[3]
            click_right = finger_data2[3]
            pos = win32api.GetCursorPos()
            if pos_move:
                pos = (pos[0] + int(rel_pos_x), pos[1] + int(rel_pos_y))
                win32api.SetCursorPos(pos)
            if click_left != last_mouse_state_left:
                last_mouse_state_left = click_left
                if click_left:
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, pos[0], pos[1], 0, 0)
                else:
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, pos[0], pos[1], 0, 0)
            if click_right != last_mouse_state_right:
                last_mouse_state_right = click_right
                if click_right:
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, pos[0], pos[1], 0, 0)
                else:
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, pos[0], pos[1], 0, 0)
                
            
            
            time.sleep(0.02)

