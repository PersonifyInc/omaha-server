from twisted.web import resource
from twisted.python import log
from db_helper import DbHelper
from config import Config
import json, re

class UncensorOutResource(resource.Resource):
  isLeaf = True
  pathFromRoot = '/service/uncensor_domains'

  def render_GET(self, request):
    macdb = DbHelper()
    
    ua = request.requestHeaders.getRawHeaders('User-Agent')
    if ua != None:
      ua = ua[0]
      matchObj = re.match( r'.*? (\(.*?\)) .*', ua)
      os = None
      version = None

      if matchObj:
        x2 = matchObj.group(1)
        os = 'win' if (x2.find('Windows') != -1) else 'mac' if (x2.find('Mac OS') != -1) else None

      matchObj = re.match( r'.* BitPop/(\d+\.\d+\.\d+\.\d+) .*', ua) # get version
      if matchObj:
        version = matchObj.group(1)

      if version and os:
        macdb.stats_add(version, os)

    res = macdb.uncensor_fetch_all()
    macdb.cleanup()
    
    request.setHeader('Content-Type', 'application/json')
    
    return json.dumps(res)
