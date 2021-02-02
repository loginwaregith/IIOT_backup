#IMPORT ALL REQUIRED MODULES
from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import exc,cast,Date,func,and_
import requests as req
import json
from datetime import datetime,timedelta,time
import RPi.GPIO as GPIO
from flask_cors import CORS, cross_origin
import configuration as config
from models import *
from adminEndpoints import admin 
from operatorScreens import operator


#VARIABLE THAT HOLDS THE HOLDING RELAY PIN NUMBER
global holdingPin 
#VARIABLE THAT HOLDS THE HOLDING STATUS / BYPASS MACHINE OR HOLD MACHINE
holdingStatus = ""


#CREATE A APP OBJECT
app = Flask(__name__)
#CREATE A CORS OBJECT
cors = CORS(app)
#CONFIGURATION OF CORS AND AND SQLALCHEMY 
app.config['CORS_HEADERS'] = config.CORS_HEADERS
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.secret_key = config.SECRET_KEY

#SQLALCHEMY DB OBJECT
db.app = app
db.init_app(app)

#REGISTER ALL THE ADMIN AND OPERATOR ENDPOINTS
app.register_blueprint(admin)
app.register_blueprint(operator)

#GET THE HOLDING PIN NUMBER AND HOLDING STATUS FROM LOCAL DATABASE
try : 
    result=otherSettings.query.get(1)
    holdingPin=int(result.holdingRelay)
    holdingStatus=result.machineBypass
    print(holdingPin)
    print(holdingStatus)
except Exception as e:
    print(e,"error getting status of holding Relay")
    #IF WE FAIL TO GET THE HOLDING CREDENTIAL THEN SET PIN 7 BY DEFAULT AS HOLDING PIN AND HOLDING STATUS AS BYPASS
    holdingPin=7
    holdingStatus="ByPass Machine"

# GET UP GPIO PINS OF RASPBERRY PI
GPIO.setmode(GPIO.BOARD)
GPIO.setup(holdingPin,GPIO.OUT)

#SHUTDOWN FEATURE 
@app.route('/shutdown', methods=['GET', 'POST'])
def shutdown():
   print("shutting down")   
   os.system("sudo shutdown -h now ") 
   return("",204)

#HOLDING MACHINE FEATURE
@app.route('/HoldMachine', methods=['POST'])
def hold_machine():
    data=request.get_json()
    state=data['State']
    if(holdingStatus=="Hold Machine"):
       if(state=='Hold'):
          print("holding machine....")
          GPIO.output(holdingPin,False)
       else:
          print("releasing machine....")
          GPIO.output(holdingPin,True) 
    else:
          #Bypass the machine
          GPIO.output(holdingPin,True)  
    return ("",204)
     
@app.route('/getCurrentSignal', methods=['GET', 'POST'])
def returnCurrentSignal():
  username=request.get_json()['userName'];
  liveSignal = "Machine Idle"
  try:
      result=liveStatus.query.get(1)
      if result is not None: 
          liveSignal=result.signalName
  except Exception as e:
      print(e,"failed to get live Status code")        
  CurrentDate=datetime.now().date()
  CurrentTime=datetime.now().time()
  endTime=time(0, 00,00)
  sihTime=time(6, 59,00)
  if(CurrentTime>=endTime and CurrentTime<=sihTime):
      filterDate=CurrentDate-timedelta(1)
  else:
      filterDate=CurrentDate
  presentDate=filterDate.strftime("%Y-%m-%d")
  print(presentDate) 
  try:  
      productionCount=db.session.query(production).filter(and_(production.status.like("1"),production.operatorName.like(username),production.date.like(presentDate))).count()
      print(result) 
      return (jsonify({'result':{"status":1,"liveSignal":liveSignal,"production":productionCount}}))
  except:
      return (jsonify({'result':{"status":0,"liveSignal":liveSignal,"production":0}}))

#START THE SERVER AT PORT 5002 
#if __name__ == "__main__":
#   app.run(port=5002,threaded=True,debug=True)





