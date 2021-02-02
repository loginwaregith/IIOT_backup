#import the library which reads all the cnc machine signals and stores in local database.
from signal_package import cncSignalsTracker
import configuration as config
import time

import multiprocessing as mp
import api as apicall
import sendData as send_data




database = config.DATABASENAME
holdMachineEndpoint = "http://" + config.LOCALSERVER_IPADDRESS + ":" + config.PORT + "/HoldMachine"
localHeaders = config.HEADERS



#create a cncSignalsTracker object
cnc = cncSignalsTracker()


   
def api_function():
    #START THE SERVER AT PORT 5002
    apicall.app.run(port=5002,threaded=True,debug=True)
        
        
def main_program():
    cnc.configure(
    databaseName = database,
    headers = localHeaders,
    holdMachineUrl = holdMachineEndpoint
        )
    cnc.getAndSetupPins()
    cnc.start()

def send_to_server():
    #continously run the loop to send data to server every 2 seconds 
    while(1):
        #Function call of 'SendLiveStatus' Function
        send_data.SendLiveStatus("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/PostMachineStatus")

        #Function call of 'SendProductionData' Function
        #send_data.SendProductionData("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/Production")

        #Function call of 'SendAlarmData' Function
        #send_data.SendAlarmData("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/AlarmInfo")
        
        #wait for 5 seconds 
        time.sleep(2)
     
#creating a multi processing objects
p1 = mp.Process(target = api_function)
p2 = mp.Process(target = main_program)
p3 = mp.Process(target = send_to_server)

p1.start()
p2.start()
p3.start()


p1.join()
p2.join()
p3.join()
