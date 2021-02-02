from flask import Blueprint,request,jsonify
from datetime import datetime,timedelta,time
from sqlalchemy import exc,cast,Date,func,and_
import requests as req
import json
import configuration as config
from models import *


import logging as log
log.basicConfig(
                    filename = "IIOT.log",
                    format   = '%(asctime)s, %(levelname)-8s [%(pathname)s:%(lineno)d] %(message)s',
                    filemode = 'a'
                   )

logger = log.getLogger()

logger.setLevel(log.DEBUG)


operator = Blueprint('operator',__name__)


@operator.route('/login', methods=['GET', 'POST'])
def login():
   machineId=request.get_json()['machineId']
   username=request.get_json()['username']
   password=request.get_json()['password']
   resultData={}
   #calculate the current shift
   
   TimeObj=datetime.now().time()
   logger.debug(f"Current Time :{str(TimeObj)}")
   query=db.session.query(ShiftData).filter(and_(func.time(ShiftData.fromTime)<=TimeObj,func.time(ShiftData.toTime)>=TimeObj)) 
   for row in query.all():  
     if(row.id==1):
         logger.info("Shift 1")
         resultData['Shift']=row.shift             
     elif(row.id==2):
         logger.info("Shift 2")
         resultData['Shift']=row.shift 
     elif(row.id==3):
         logger.info("Shift 3")
         resultData['Shift']=row.shift                         
     else: 
         pass

   #check for admin user 
   if(username=="admin" and password=="IIotAdmin"):
         return jsonify({"result": {"status":1,"admin":True,"message":"success"}})   

   #check for a valid user or no       
   loginUrl="http://" + config.SERVER_IP + config.SERVER_ENDPOINT_START + "/Login"
   headers = config.HEADERS 
   try:
         res=req.post(loginUrl,headers=headers,data=json.dumps({"UserID":username,"Password":password,"MachineCode":machineId}),timeout=4)     
         componentList=[]
         modelList=[]
         #operationList = []
         data=res.json()
         logger.debug(f"{data}")
         if(data['Error']!=None):
              debug.error("error")    
              return jsonify({"result": {"status":0,"admin":False,"message":"invalid username or password"}}) 
         else:
              resultData['FullName']=data['FullName']
              data1=data['Components']
              data2=data['ProductModels']
              #data3 = data['Operations']
              for datas in data1:
                 componentList.append(datas['Code'])
              for datas in data2:
                 modelObj={}
                 modelObj['code']=datas['Code']
                 modelObj['value']=datas['Value']   
                 modelList.append(modelObj)
              #for datas in data3:
              #   operationList.append(datas['Code'])
              resultData['Components']=componentList
              resultData['Models']=modelList
              #resultData['Operations']=operationList
              logger.debug(f"{resultData}")
              return jsonify({"result": {"status":1,"admin":False,"message":"success","data":resultData}})      
   except Exception as e:
         logger.error(f"error while connecting to server for login details {e}")
         return jsonify({"result": {"status":0,"admin":False,"message":"Something Went Wrong, Check Network Connection"}})

             
@operator.route('/', methods=['GET', 'POST'])
def loadScreen():
   #save shift data to databse
   try:
       url="http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/ShiftList"
       logger.debug(f"{url}")
       (url)     
       res=req.get(url,timeout=4)
       datas=res.json()
       for data in datas: 
          idNew=data['ID']
          shiftNew=data['Name']
          fromTimeNew=data['FromTime']
          toTimeNew=data['ToTime']
          fromTimeNew=datetime.strptime(fromTimeNew,"%Y-%m-%dT%H:%M:%S")
          toTimeNew=datetime.strptime(toTimeNew,"%Y-%m-%dT%H:%M:%S")
          shiftObj=ShiftData(id=idNew,shift=shiftNew,fromTime=fromTimeNew,toTime=toTimeNew)
          try:
             result=ShiftData.query.filter_by(id=idNew).scalar() 
             if(result!=None):
                 pass
             else:    
                db.session.add(shiftObj)
                db.session.commit()
                logger.info("added shift data to database") 
          except Exception as e:
             logger.error(f"{e}")
                     
   except:
       logger.error("something went wrong while getting shift data....")

   #response data will be stored in this variable
   #fetch all the reasons for the alarm signal from server
   # try:
   #   url="http://+config.SERVER_IP+ config.SERVER_ENDPOINT_START +"/GetAlarmReasonsList"      
   #   res=req.get(url,timeout=2)
   #   datas=res.json()
   #   print(datas)
   #   result=alarmReasons.query.get(id=1)
   #   if(result!=None):
   #      for data in datas:
   #         reasonsObj=alarmReasons(reasons=data['Reasons'])
   #         db.session.add(reasonsObj)
   #         db.session.commit()
   # except Exception as e:
   #    print("something went wrong with alarm reasons",e)     
    
   #load all the other settings data like machineId,idleTimeout from local db to store in session variable      
   data={}
   try:
      result=otherSettings.query.get(1)
      if(result!=None):
          data['machineId']=result.machineId
          data['idleTimeout'] = result.idleTimeout
          data['batchSize']= result.batchSize
          holdingPin = result.holdingRelay
      else:
          logger.debug("no other settings data in database")
      return jsonify({"result": {"message":"success","status":1,"data":data}})      
   except Exception as e:
      logger.error(f"{e}")
      return jsonify({"result": {"messgae":"something went wrong","status":0,"data":{}}})



@operator.route("/operator", methods=["GET", "POST"])
def operatorScreen():
    result=request.get_json()
    shift=result['shift']
    username=result['fullName']
    component=result['componentName']
    model=result['modelName']
    operation=result['operationName']  
    machineId=result['machineId']
    jobId=result['jobId']
    #calculate the current shift
    TimeObj=datetime.now().time()
    query=db.session.query(ShiftData).filter(and_(func.time(ShiftData.fromTime)<=TimeObj,func.time(ShiftData.toTime)>=TimeObj)) 
    for row in query.all():
         if(row.id==4 or row.id==5):
            pass
         elif(row.id==1):
            logger.info("Shift 1")
            nowShift=row.shift 
         elif(row.id==2):
            logger.info("Shift 2")
            nowShift=row.shift 
         elif(row.id==3):
            logger.info("Shift 3")
            nowShift=row.shift                         
         else: 
            nowShift="Second" 

    timeObj = datetime.now()
    time1=timeObj.strftime("%Y/%m/%d %H:%M:%S")
    CurrentDate=datetime.now().date()
    CurrentTime=datetime.now().time()
    #print(type(CurrentTime))
    sihTime=time(6,59,59)
    if(CurrentTime<=sihTime):
         date=CurrentDate-timedelta(1)
    else:
         date=CurrentDate
    presentDate=date.strftime("%Y-%m-%d")
    productionObj=production(operatorName=username,jobId=jobId,shift=shift,component=component,modelName=model,operation=operation,cycleTime="5.5",inspectionStatus="0",status="0",timeStamp=time1,machineId=machineId,date=presentDate)
    try:
         db.session.add(productionObj)
         db.session.commit()
         logger.info("inserting into databse")
    except Exception as e:
         logger.error(f"{e}")
    try:
         # print("releasing machine")
         releaseUrl="http://"+config.LOCALSERVER_IPADDRESS+":"+config.PORT+"/HoldMachine"
         headers = config.HEADERS
         res=req.post(releaseUrl,headers=headers,data=json.dumps({"State":"Release"}),timeout=2)         
         return jsonify({"result": {"status":1,"message":"job Status Ok , proceed to cycle ","data":{"shift":nowShift}}})
    except :
         return jsonify({"result": {"status":0,"message":"something went wrong please fill details once more","data":{}}})


@operator.route('/alarmScreen', methods=['GET','POST'])
def alarmScreen():
    result=request.get_json()
    shift=result['shift']
    username=result['fullName']
    component=result['componentName']
    model=result['modelName']
    operation=result['operationName']  
    machineId=result['machineId']    
    reason=result['alarmReason']
    if result['jobId'] != "":
        jobId=result['jobId']
    else:
        jobId="No Job Placed"
    timeObj = datetime.now()
    time=timeObj.strftime("%Y/%m/%d %H:%M:%S")
    alarmObj=alarm(operatorName=username,jobId=jobId,shift=shift,component=component,modelName=model,operation=operation,timeStamp=time,machineId=machineId,reason=reason) 
    try:
         db.session.add(alarmObj)
         db.session.commit()
         logger.info("inserting into database")
    except Exception as e:
         logger.error(f"{e}")   
         db.session.rollback()
         return jsonify({"result": {"status":0,"message":"something went wrong"}})
    
    releaseUrl="http://"+config.LOCALSERVER_IPADDRESS+":"+config.PORT+"/HoldMachine"
    headers = config.HEADERS
    try:
          res=req.post(releaseUrl,headers=headers,data=json.dumps({"State":"Release"}),timeout=2)
          logger.debug(f"{res.status_code}")
    except:
          logger.error("error..")  
          return jsonify({"result": {"status":0,"message":"something went wrong"}})   
    return jsonify({"result": {"status":1,"message":"successfully data saved"}})


@operator.route('/idleTimeout', methods=['GET','POST'])
def IdleTimeout():
    result=request.get_json()
    shift=result['shift']
    username=result['fullName']
    component=result['componentName']
    model=result['modelName']
    operation=result['operationName']  
    machineId=result['machineId']
    reason=result['idleReason']
    timeObj = datetime.now()
    time=timeObj.strftime("%Y/%m/%d %H:%M:%S")
    idleTimeoutObj=idleTimeout(operatorName=username,shift=shift,component=component,modelName=model,operation=operation,timeStamp=time,machineId=machineId,reason=reason) 
    try:
        db.session.add(idleTimeoutObj)
        db.session.commit()
        logger.info("inserting into database")
    except Exception as e:
        logger.error(f"{e}")
        return jsonify({"result": {"status":0,"message":"something went wrong"}})

    releaseUrl="http://"+config.LOCALSERVER_IPADDRESS+":"+config.PORT+"/HoldMachine"
    headers = config.HEADERS
    try:
          res=req.post(releaseUrl,headers=headers,data=json.dumps({"State":"Release"}),timeout=2)
          logger.debug(f"{res.status_code}")
          
    except:
           logger.error("error..") 
           return jsonify({"result": {"status":0,"message":"something went wrong"}})   
    return jsonify({"result": {"status":1,"message":"successfully data saved"}})

