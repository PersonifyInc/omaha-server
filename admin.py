#   Copyright (C) 2011 Crystalnix <vgachkaylo@crystalnix.com>

#   This file is part of omaha-server.

#   omaha-server is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   omaha-server is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with omaha-server.  If not, see <http://www.gnu.org/licenses/>.

from twisted.web import resource
from config import Config
from new_full import NewFullResource
from new_delta import NewDeltaResource
from switch import SwitchResource
#from mac_update import MacUpdateManager
from db_helper import DbHelper
from new_mac_full import NewMacFullResource
from mac_edit import MacEditResource
from mac_delete import MacDeleteResource
from uncensor_manage import UncensorManageResource
from uncensor_proxy_manage import UncensorProxyManageResource
from util import *
import os

class UpdateManager(resource.Resource):
    isLeaf = False
    pathFromRoot = '/service/admin'

    def __init__(self):
        resource.Resource.__init__(self)
        self.newFull = NewFullResource()
        self.putChild('new_full', self.newFull)
        self.newDelta = NewDeltaResource()
        self.putChild('new_delta', self.newDelta)
        self.switch = SwitchResource()
        self.putChild('switch', self.switch)
        
        self.mac = resource.ForbiddenResource()
        self.newMacFull = NewMacFullResource()
        self.mac.putChild('new_full', self.newMacFull)
        self.macEdit = MacEditResource()
        self.mac.putChild('edit', self.macEdit)
        self.macDelete = MacDeleteResource()
        self.mac.putChild('delete', self.macDelete)
        self.putChild('mac', self.mac)
        
        self.uncensor_manage = UncensorManageResource()
        self.putChild('uncensor', self.uncensor_manage)

        self.uncensor_proxy_manage = UncensorProxyManageResource()
        self.putChild('uncensorp', self.uncensor_proxy_manage)

        self.putChild('', self)

    def render_GET(self, request):
        macdb = DbHelper()
        
        mainDict = loadJsonAndCheckIfLatestKeyExists(Config.bitpopUpdateInfoFile)
        bitpopInfo = mainDict['jsonData']
        latestExists = mainDict['latestExists']

        output = """<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="chrome=1">

    <title>House of Life Update Manager</title>

    <!-- CSS: implied media="all" -->
    <link rel="stylesheet" href="/css/style.css?v=2">
</head>
<body>
    <div id="container">
        <header>
            <h1>House of Life Update Manager</h1>
            <p>Copyright &copy; 2011, House of Life Property ltd. All rights reserved.<br />
               Copyright &copy; 2011, Crystalnix &lt;vgachkaylo@crystalnix.com&gt;</p>
        </header>
        <div id="main" role="main">
          <section id="win_updates">"""

        output += """
            <h2>BitPop <img src="/img/windows-logo.png" alt="Windows logo" /></h2>"""
        if not latestExists:
            output += """
            <p>There are no BitPop Windows updates available.</p>"""
        else:
            output += """
            <p>Latest BitPop version: {0}</p>""".format(bitpopInfo["latest"])
            output += """
            <h3>Update files</h3>
            <ul>
                <li><a href="{0}">full update v{1}</a></li>""".format(getUpdateURL(bitpopInfo['latest']),
                                                                      bitpopInfo['latest'])
            if bitpopInfo.has_key('delta') and type(bitpopInfo['delta']) == type([]):
                for deltaFromVersion in bitpopInfo['delta']:
                    output += """
                <li><a href="{0}">delta update from v{1}</a></li>""".format(
                        getUpdateURL(bitpopInfo['latest'], deltaFromVersion),
                        deltaFromVersion)
        output += """
            </ul>"""

        bitpopNewDict = loadJsonAndCheckIfLatestKeyExists(Config.bitpopNewUpdateInfoFile)
        bitpopNewInfo = bitpopNewDict['jsonData']
        bitpopNewLatestExists = bitpopNewDict['latestExists']

        if not bitpopNewLatestExists:
            output += """
            <p><a href="{0}">Add new full version installer</a></p>""".format(self.pathFromRoot + '/new_full')
        else:
            output += """
            <h3>Uploaded new version {0}</h3>""".format(bitpopNewInfo['latest'])
            if bitpopNewInfo.has_key('delta') and type(bitpopNewInfo['delta']) == type([]):
                output += """
                <ul>"""
                for newDeltaFrom in bitpopNewInfo['delta']:
                    output += """
                    <li>delta from {0}</li>""".format(newDeltaFrom)
                output += """
                </ul>"""
            output += """
            <p><a href="{0}">Add new delta update installer</a></p>
            <p><a href="{1}">Switch to new version ({2})</a></p>""".format(
                self.pathFromRoot + '/new_delta', self.pathFromRoot + '/switch', bitpopNewInfo['latest'])
        output += """
            <p>
                <form style="display:none" id="clear_all" method="POST">
                  <input type="hidden" name="action" value="delete" />
                </form>
                <a href="javascript:void(0)" onclick="(function () { document.getElementById('clear_all').submit();})()">
                   Clear all updates
                </a>
            </p>
          </section>
          <section id="mac_updates">
            <h2>BitPop <img src="/img/apple-logo.png" alt="Apple logo" /></h2>"""

        macUpdates = macdb.fetch_several_latest(5)
        if len(macUpdates) != 0:
          output += """
            <p>Latest BitPop version: {0}</p>""".format(macUpdates[0]["version"])
          output += """
            <h3>Update files:</h3>
            <ul>"""
          
          activeVersion = None
          try:
            activeStream = open(Config.macActiveVersionFile, "r")
            try:
              activeVersion = activeStream.readline()
            finally:
              activeStream.close()
          except IOError:
            pass
          
          for upd in macUpdates:
            output += """
              <li><a href="{0}">full update v{1}{2}</a>""".format(getUpdateURLMac(upd['dmg_path']),
                                                                  upd['version'],
                                                                  ' (*)' if upd['version'] == activeVersion 
                                                                         else ''
                                                                 )
            output += """
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                  <a href="/service/admin/mac/edit/{0}">Edit</a> |
                  <a href="/service/admin/mac/delete/{0}"
                    onclick="javascript: return confirm('Are you sure you want to delete this version?');">
                      Delete
                  </a>""".format(upd['id'])
          output += """
            </ul>"""
#          if macUpdates[0]['version'] != activeVersion:
#            output += """
#            <p><a href="{0}">Make latest version active
        else:
          output += """
            <p>There are no BitPop mac updates available.</p>"""

        output += """            
            <p><a href="{0}">Add new version archive</a></p>""".format(self.pathFromRoot + '/mac/new_full')
        output += """
          </section>
        </div>
        <footer>
        </footer>
    </div>
</body>
</html>"""
        macdb.cleanup()
        return output
        
    def render_POST(self, request):
        if ('action' in request.args) and (request.args['action'][0] == 'delete'):
            try:
                os.remove(Config.bitpopUpdateInfoFile)
            except OSError:
                pass
            try:
                os.remove(Config.bitpopNewUpdateInfoFile)
            except OSError:
                pass
                
            request.setResponseCode(301)
            request.setHeader('Location', self.pathFromRoot)
        else:
            request.setResponseCode(400)
            return 'Bad request'
        
        return 'OK'
