import requests as req
import json

import logging as log
log.basicConfig(
                    filename = "IIOT.log",
                    format   = '%(asctime)s, %(levelname)-8s [%(pathname)s:%(lineno)d] %(message)s',
                    filemode = 'a'
                   )

logger = log.getLogger(__name__)

logger.setLevel(log.DEBUG)


def holdMachine(self,):
      HOLD_MACHINE_URL = self.HOLD_MACHINE_URL
      LOCAL_HEADER = self.HEADERS
      try:
            result=req.post(HOLD_MACHINE_URL,json.dumps({"State":"Hold"}),headers=LOCAL_HEADER,timeout=2)
            logger.debug("holding machine")                
      except Exception as e:
            logger.error(f"{e}")