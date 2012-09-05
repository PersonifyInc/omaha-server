from twisted.web import resource
from db_helper import DbHelper
from config import Config
from util import *
from time import strftime
from datetime import datetime

class MacFeedResource(resource.Resource):
  isLeaf = True
  pathFromRoot = '/service/mac_feed'
  
  def render_GET(self, request):
    request.setHeader('Content-Type', 'application/rss+xml')
    macdb = DbHelper()
    items = macdb.fetch_several_latest(5)
    
    output = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0" xmlns:sparkle="http://www.andymatuschak.org/xml-namespaces/sparkle"  xmlns:dc="http://purl.org/dc/elements/1.1/">
       <channel>
          <title>BitPop Update Feed</title>
          <link>"""
    output += Config.insecureDomain + self.pathFromRoot
    output += """</link>
          <description>List of BitPop packages with different versions.</description>
          <language>en</language>"""
    
    if len(items) > 0:
      for item in items:
        output += """
             <item>
                <title>Version {0}</title>
                <description><![CDATA[
                  {1}
                ]]></description>
                <pubDate>{2}</pubDate>
                <enclosure url="{3}" sparkle:version="{0}" length="{4}" type="application/octet-stream" sparkle:dsaSignature="{5}" />
             </item>""".format(item['version'], item['rel_notes'], 
                               strftime("%a, %d %b %Y %H:%M:%S +0000", 
                                  datetime.utcfromtimestamp(item['pub_ts']).timetuple()), 
                               getUpdateURLMac('BitPop-' + item['version'] + '.dmg'),
                               item['dmg_size'], item['dsa_signature'])
    output += """
       </channel>
    </rss>
"""
    
    macdb.cleanup()
    
    return output
