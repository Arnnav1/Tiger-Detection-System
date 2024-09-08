import telepot
#from pprint import pprint
import time
from pyembedded.raspberry_pi_tools.raspberrypi import PI
import cv2
from picamera2 import Picamera2
from ultralytics import YOLO
import io
import subprocess
import RPi.GPIO as GPIO
#global chat_id

tiger_pin = 11
heating_pin = 13
wifi_pin = 15

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(tiger_pin, GPIO.OUT)
GPIO.setup(heating_pin, GPIO.OUT)
GPIO.setup(wifi_pin, GPIO.OUT)

time.sleep(20)
chat_id = 
Token = ""
bot = telepot.Bot(Token)
bot.sendMessage(chat_id, "System booting ........")

pi = PI()
pi_param = {
	'ram_info' : pi.get_ram_info(),
	'disk_space' : pi.get_disk_space(),
	'cpu_usage' : pi.get_cpu_usage(),
	'ip_add' : pi.get_connected_ip_addr(network='wlan0'),
	'cpu_temp' :  pi.get_cpu_temp(),
	'wifi_status' : pi.get_wifi_status()
	}

picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 720)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

#model = YOLO("best_train7.pt")
model = YOLO("/home/pi/tiger_detection/best_train7_ncnn_model")
#model = YOLO("./best.pt")

def handle (msg):
    global chat_id
    chat_id = msg['chat']['id']
    command = msg['text']
    print(chat_id)
    print(command)

    if command == '/start':
        bot.sendMessage(chat_id, "tiger dection system started")

    if command == '/shutdown':
        bot.sendMessage(chat_id, "System shutdowning")
        subprocess.run(["sudo", "shutdown", "-h", "now"])
    
    if command == '/reboot':
        bot.sendMessage(chat_id, "System rebooting")
        subprocess.run(["sudo", "shutdown", "-r", "now"])
    
    if command == '/help':
        bot.sendMessage(chat_id, '''These are some commands to operate the system:
        /start
        /help
        /photo
        /system
        /reboot
        /shutdown''')
    
    if command == '/photo':
        _,image = cv2.imencode('.jpeg', annotated_frame)
        inmemoryfile = io.BytesIO(image)
        bot.sendPhoto(chat_id,photo=inmemoryfile,caption = time.strftime("%Y-%m-%d-%H:%M:%S")) 
        inmemoryfile.close()
        
    if command == '/system':
        bot.sendMessage(chat_id , pi_param)
    
    if command not in ('/hi','/help','/photo','/system','/reboot','/shutdown'):
        bot.sendMessage(chat_id, "Give an valid command or use /help")

bot.message_loop(handle)

print("I am listening")

def network():
  """Checks if the Raspberry Pi is connected to Wi-Fi."""

  try:
    output = subprocess.check_output(["iwconfig", "wlan0"])
    if "ESSID" in output.decode("utf-8"):
      return True
    else:
      return False
  except subprocess.CalledProcessError:
    return False

if network():
    bot.sendMessage(chat_id, "Connected to internet!")
    GPIO.output(wifi_pin, True)

else:
    GPIO.output(wifi_pin, False)

while 1:
    #time.sleep(10)
    #bot.sendMessage(chat_id,"return from while loop")
    frame = picam2.capture_array()
    results = model(frame, conf = 0.8)
    annotated_frame = results[0].plot()
    #cv2.imshow("Camera", annotated_frame)
    if len(results[0].boxes.conf) > 0 and results[0].boxes.conf > 0.8 :
        
        bot.sendMessage(chat_id,"tiger detected")
        _,image = cv2.imencode('.jpeg', annotated_frame)
        inmemoryfile = io.BytesIO(image)
        bot.sendPhoto(chat_id,photo=inmemoryfile,caption = time.strftime("%d-%m-%Y-%H:%M:%S"))
        GPIO.output(tiger_pin, True)
        inmemoryfile.close()
    
    if len(results[0].boxes.conf) == 0:
        GPIO.output(tiger_pin, False)
    
    if pi_param['cpu_temp'] > 80 :
        GPIO.output(heating_pin, True)
        bot.sendMessage(chat_id,"Pi over heating")
    if pi_param['cpu_temp'] < 80:
        GPIO.output(heating_pin, False)
'''
    if cv2.waitKey(1) == ord("q"):
        break

cv2.destroyAllWindows()

#print(bot.getMe())
'''