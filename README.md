# eteeMouse

Use your new eteeController as a Mouse.

**Currently Windows only!** Feel free to help me use pyautogui for any other system. And yes I know, this code is ugly. Wanted to test the API and now my eteeController is a mouse.

## Controls

- Trackpad is used for moving mouse
- Index finger for left mouse button
- Middle finger for right mouse button

## How to use

- Follow [etee-Python-API](https://github.com/eteeXR/etee-Python-API) guide for installing Python package
- Active above created venv
- Execute `pip install pywin32 pyautogui`
- Execute `python print_etee_mouse.py`
- Press `Esc` in (i.e.) PowerShell to exit script

## What can I change?

- Line 9: which controller should be used
- Line 10: which finger is left click
- Line 11: which finger is right click
- Line 12: some random number used as a multiplier
- Line 13: poll_rate (not exact but good enough)

## Image(s)

![Default PowerShell Output](https://github.com/lischetzke/eteeMouse/blob/main/image01.png?raw=true)
