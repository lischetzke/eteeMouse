import time
import sys
import os
import keyboard
from datetime import datetime
import win32api, win32con
from etee import EteeController

controller_selected = "right"
finger_left = "index"
finger_right = "middle"
mouse_speed_multiplier = 0.2
poll_rate = 50 # results in round about 50 updates per second

def console_move (y, x):
    print("\033[%d;%dH" % (y, x))

def console_cls():
    os.system('cls' if os.name=='nt' else 'clear')

def printProgressBar (iteration, total, suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'|{bar}| {percent}% {suffix}', end = printEnd)

fin_l1 = finger_left + "_pull"
fin_l2 = finger_left + "_force"
fin_l3 = finger_left + "_touched"
fin_l4 = finger_left + "_clicked"
fin_r1 = finger_right + "_pull"
fin_r2 = finger_right + "_force"
fin_r3 = finger_right + "_touched"
fin_r4 = finger_right + "_clicked"

def process_controller(dev):
    loc = [etee.get_data(dev, "trackpad_x"), etee.get_data(dev, "trackpad_y")]
    pressure = [etee.get_data(dev, "trackpad_pull"), etee.get_data(dev, "trackpad_force"),
                etee.get_data(dev, "trackpad_touched"), etee.get_data(dev, "trackpad_clicked")]
    finger_data1 = [etee.get_data(dev, fin_l1), etee.get_data(dev, fin_l2),
                    etee.get_data(dev, fin_l3), etee.get_data(dev, fin_l4)]
    finger_data2 = [etee.get_data(dev, fin_r1), etee.get_data(dev, fin_r2),
                    etee.get_data(dev, fin_r3), etee.get_data(dev, fin_r4)]
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

    last_mouse_state_left = False
    last_mouse_state_right = False
    pending_movement_x = 0
    pending_movement_y = 0

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
            print(f"Finger left click: {finger_left}")
            print(f"Finger right click: {finger_right}")
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
            print(f">>>>> FINGER {finger_left.upper()} <<<<<")
            print(f"Pull  ", end = "")
            printProgressBar(finger_data1[0], 126, printEnd="\n")
            print(f"Force ", end = "")
            printProgressBar(finger_data1[1], 126, printEnd="\n")
            print(f"| Touch    | Press    |")
            print(f"{'|          |██████████|' if finger_data1[3] else '|██████████|          |' if finger_data1[2] else '|          |          |'}")
            print()
            print(f">>>>> FINGER {finger_right.upper()} <<<<<")
            print(f"Pull  ", end = "")
            printProgressBar(finger_data2[0], 126, printEnd="\n")
            print(f"Force ", end = "")
            printProgressBar(finger_data2[1], 126, printEnd="\n")
            print(f"| Touch    | Press    |")
            print(f"{'|          |██████████|' if finger_data2[3] else '|██████████|          |' if finger_data2[2] else '|          |          |'}")
            print()
            pos_x = selected_loc[0] - 126
            pos_y = -(selected_loc[1] - 126)
            pos_pressure = selected_pressure[0] / 126
            pos_move = selected_pressure[2]
            rel_pos_x = pos_x * pos_pressure * mouse_speed_multiplier
            rel_pos_y = pos_y * pos_pressure * mouse_speed_multiplier
            click_left = finger_data1[3]
            click_right = finger_data2[3]
            pos = win32api.GetCursorPos()
            if pos_move:
                pending_movement_x += rel_pos_x
                pending_movement_y += rel_pos_y
            if int(pending_movement_x) != 0 or int(pending_movement_y) != 0:
                movement_x = int(pending_movement_x)
                pending_movement_x -= movement_x
                movement_y = int(pending_movement_y)
                pending_movement_y -= movement_y
                pos = (pos[0] + movement_x, pos[1] + movement_y)
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
            print(f"| {'rel_pos_x':>10} | {'rel_pos_y':>10} | {'pending_mov_x':>15} | {'pending_mov_y':>15} |")
            print(f"| {rel_pos_x:>10.5f} | {rel_pos_y:>10.5f} | {pending_movement_x:>15.5f} | {pending_movement_y:>15.5f} |")
            print(f"|{'-'*61}|")
            print(f"| {'mouse_left':>12} | {'mouse_right':>12} |")
            print(f"| {click_left:>12} | {click_right:>12} |")
            
            time.sleep(1 / poll_rate)
