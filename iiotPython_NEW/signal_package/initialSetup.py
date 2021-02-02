from ._globalVariables import LIVE_STATUS_CODES
import sqlite3 as sqlite
from sendData import curs2,conn2
import logging as log

log.basicConfig(
                    filename = "IIOT.log",
                    format   = '%(asctime)s, %(levelname)-8s [%(pathname)s:%(lineno)d] %(message)s',
                    filemode = 'a'
                   )

logger = log.getLogger()
logger.setLevel(log.DEBUG)


def configure(self,databaseName,headers,holdMachineUrl):
    self.DATABASE_NAME = databaseName
    self.HEADERS =  headers
    self.HOLD_MACHINE_URL = holdMachineUrl
    #make the database connection 
    databaseConnection(self,databaseName)
    logger.info("Configuration done.....")
    return

def databaseConnection(self,database):
    if conn2:
        logger.info("ESTABLISHED CONNECTION SUCESSFULLY WITH DATABASE")
        #call getMachineIdFunction 
        loadMachineNameFromDB(self,)
        #call the initialSetupFunction
        initialSetup(self,)
        return

    else:
        logger.error("FAILED TO ESTABLISH CONNECTION WITH DATABASE")
        return None    


def initialSetup(self,):
   machineId=self.machineId
   try:
      curs2.execute("select * from live_status")
      result=curs2.fetchone()[0]
      if result!=1:
         query="insert into live_status(machineId,machineType,status,color,signalName)values(?,?,?,?,?)"
         values=(machineId,"Automatic",LIVE_STATUS_CODES['machineIdle'],"orange","alarmON")
         curs2.execute(query,values)
         conn2.commit()
         logger.info("live Status is set for the initial time")
      else:
         logger.debug("already the row exists")
   except Exception as e:
      logger.error(f"failed to insert to liveStatus for the initial time {e}")


#GET THE MACHINE NAME FROM THE LOCAL DATABASE
def loadMachineNameFromDB(self,):
   curs2.execute("select * from other_settings")
   self.machineId=curs2.fetchone()[1]
   logger.debug(f"machine Id set as ={self.machineId}")
   return
   
