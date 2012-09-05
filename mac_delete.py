from twisted.web import resource
from db_helper import DbHelper
from config import Config
import re, os

class MacDeleteResource(resource.Resource):
  pathFromRoot = "/service/admin/mac/delete"
  isLeaf = True  
  
  def render_GET(self, request):
    tr = re.compile('.*/(\d*)$')
    m = re.match(tr, request.path)
    if len(m.groups()) == 0:
      request.setResponseCode(400) # Bad request
      return "Error: Bad request."
    update_id = m.groups()[0]
    
    macdb = DbHelper()
    upd = macdb.fetch_by_id(int(update_id))
    
    if upd == None:
      request.setResponseCode(404) # Bad request
      return "Error: Not found."
      
    macdb.delete(int(update_id))
    
    try:
      activeStream = open(Config.macActiveVersionFile, 'r')
      try:
        vt = activeStream.readline().strip(' \t\n\r')
      finally:
        activeStream.close()

      if vt == upd['version']:
        newLatest = macdb.fetch_latest()
        if newLatest == None:
          #delete file
          os.remove(Config.macActiveVersionFile)
        else:
          activeStream = open(Config.macActiveVersionFile, 'w')
          try:
            activeStream.write(newLatest['version'] + '\n')
          finally:
            activeStream.close()
          
    except IOError:
      pass
    
    macdb.cleanup()
        
    return """<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="refresh" content="3;url=/service/admin">
  <title>Release notes changed</title>
</head>
<body>
  <h1>Success</h1>
  <p>Record has been deleted successfully. You will be redirected in 3 seconds.</p>
</body>
</html>
"""
