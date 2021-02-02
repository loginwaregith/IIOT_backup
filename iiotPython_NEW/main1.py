#import the library which reads all the cnc machine signals and stores in local database.
from signal_package import cncSignalsTracker
import configuration as conf
#importing api.py and sendData.py to creat paralell process
import api as api_run
import sendData as sendData_run
from time import sleep
#importing multiprocessing library
import multiprocessing as mp  

database = conf.DATABASENAME
holdMachineEndpoint = "http://" + conf.LOCALSERVER_IPADDRESS + ":" + conf.PORT + "/HoldMachine"
localHeaders = conf.HEADERS

#create a cncSignalsTracker object
cnc = cncSignalsTracker()

def process_of_api():
    #start the server at port 5002
    api_run.app.run(port=5002,threaded=True,debug=True)

#pass the configuration paramters 
#get all pin numbers from local db and assign it to raspberry pi
#starts the process of collecting signals from cnc machine

def process_of_main():
    cnc.configure(
        databaseName = database,
        headers = localHeaders,
        holdMachineUrl = holdMachineEndpoint
    )
    cnc.getAndSetupPins()
    cnc.start()
 
def process_of_sendData():
    #continously run the loop to send data to server every 2 seconds 
    while(1):

        #Function call of 'SendLiveStatus' Function
        sendData_run.SendLiveStatus("http://"+conf.SERVER_IP+conf.SERVER_ENDPOINT_START+"/PostMachineStatus")

        #Function call of 'SendProductionData' Function
        sendData_run.SendProductionData("http://"+conf.SERVER_IP+conf.SERVER_ENDPOINT_START+"/Production")

        #Function call of 'SendAlarmData' Function
        #sendData_run.SendAlarmData("http://"+conf.SERVER_IP+conf.SERVER_ENDPOINT_START+"/AlarmInfo")
        
        #wait for 2 seconds 
        sleep(2)


#Creating a multiprocesses of function
p1 = mp.Process(target = process_of_api)
p2 = mp.Process(target = process_of_main)
p3 = mp.Process(target = process_of_sendData)

#Start executing the code inside the target function parllelly
p1.start()
p2.start()
p3.start()

#wait untill the complition of processes

p1.join()
p2.join()
p3.join()

