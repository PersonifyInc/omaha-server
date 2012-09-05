from twisted.web import resource
from db_helper import DbHelper
from config import Config
import json
from twisted.web.client import getPage
from twisted.web import server
import pycountry
import pygeoip



class UncensorPOutResource(resource.Resource):
  isLeaf = True
  pathFromRoot = '/service/uncensorp_domains'

  def render_GET(self, request):
    gi = pygeoip.GeoIP('GeoIP.dat', pygeoip.MEMORY_CACHE)
    country_code = gi.country_code_by_addr(request.getHeader('x-forwarded-for'))

    macdb = DbHelper()
    res = macdb.uncensorp_fetch_by_iso(country_code)
    res = { 'domains': [rec['domain'] for rec in res], 'country_code': country_code,
            'country_name': pycountry.countries.get(alpha2=country_code).name.encode('utf-8') }
    macdb.cleanup()

    request.setHeader('Content-Type', 'application/json')

    return json.dumps(res)
  
