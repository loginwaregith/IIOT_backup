#GETTTING ALL THE ACTUAL PIN NUMBERS FROM DATABASE
import RPi.GPIO as GPIO
from sendData import curs2,conn2
import logging as log

log.basicConfig(
                    filename = "IIOT.log",
                    format   = '%(asctime)s, %(levelname)-8s [%(pathname)s:%(lineno)d] %(message)s',
                    filemode = 'a'
                   )

logger = log.getLogger()
logger.setLevel(log.DEBUG)

def getAndSetupPins(self):
   logger.debug("FETCHING THE PINS AND SIGNAL NAMES FROM THE DATABASE.....")
   curs2.execute("SELECT * FROM pinout")
   for row in curs2.fetchall():
      if(row[2]=="machine"):
          self.machineSignalInputPin=int(row[3]) 
      elif(row[2]=="cycle"):
          self.cycleSignalInputPin=int(row[3])
      elif(row[2]=="alarm"):
          self.alarmSignalInputPin=int(row[3])
      elif(row[2]=="emergency"):
          self.emergencySignalInputPin=int(row[3])
      elif(row[2]=="reset"):
          self.resetSignalInputPin=int(row[3])
      elif(row[2]=="m30"):
          self.m30SignalInputPin=int(row[3])
      elif(row[2]=="runoutnotok"):
          self.runOutNotOkSignalInputPin=int(row[3])
      elif(row[2]=="spindle"):
          self.spindleSignalInputPin=int(row[3])   
   logger.info("Initilizing the gpio pins of raspberry pi .....")
   GPIO.setmode(GPIO.BOARD)
   GPIO.setup(self.machineSignalInputPin,GPIO.IN)
   GPIO.setup(self.cycleSignalInputPin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
   GPIO.setup(self.m30SignalInputPin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
   GPIO.setup(self.emergencySignalInputPin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
   GPIO.setup(self.resetSignalInputPin,GPIO.IN)
   GPIO.setup(self.alarmSignalInputPin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
   GPIO.setup(self.runOutNotOkSignalInputPin,GPIO.IN)
   GPIO.setup(self.spindleSignalInputPin,GPIO.IN)
   #setting gpio set warnings false 
   GPIO.setwarnings(False)

