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

import time
from datetime import date
from xml.dom import Node
from twisted.web import resource
from twisted.python import log
from config import Config
from util import *
import os
from xml.dom.minidom import parseString

class UpdateXMLProcessor(resource.Resource):
    isLeaf = True
    # NB!: do not use the following UUIDs
    # they are already in use for identifying software packages
    # use uuidgen.exe on Windows to generate new UUIDs
    # updaterAppId="{430FD4D0-B729-4F61-AA34-91526481799D}"
    # bitpopAppId="{8A69D345-D564-463C-AFF1-A69D9E530F96}"
    updaterAppId = '{978c0827-abe1-4b83-838e-e5763f6e3e14}'
    bitpopAppId =  '{50bc847d-ac5b-4889-9363-d602fd6f060e}'
    validAppIds=set([updaterAppId, bitpopAppId])

    def render_POST(self, request):
        request.setHeader('Content-Type', 'application/xml')

        xmlString = request.content.read()
        doc = parseString(xmlString)

        # create template output XML document
        # calculate elapsed seconds from day start
        curTime = time.mktime(time.localtime())
        dayTime = time.mktime(date.today().timetuple())
        
        outXmlString = """<?xml version="1.0" encoding="UTF-8"?>
<gupdate xmlns="http://www.google.com/update2/response" protocol="2.0">
  <daystart elapsed_seconds="%d"/>
</gupdate>""" % (curTime - dayTime)
        outDoc = parseString(outXmlString)

        attr = ['version', 'ismachine', 'machineid', 'userid', 'requestid']
        context = dict(zip(attr, map(doc.documentElement.getAttribute, attr)))

        for node in doc.getElementsByTagName('o:os'):
            osInfo = (node.getAttribute('platform'),
                      node.getAttribute('version'),
                      node.getAttribute('sp'))
            #log.msg("OS platform=%s, version=%s, sp=%s" % osInfo)
            context['os'] = dict(zip(['platform', 'version', 'sp'], osInfo))
            break

        for appElement in doc.getElementsByTagName('o:app'):
            appContextAttr = ['appid', 'version']
            appContext = dict(zip(appContextAttr, map(appElement.getAttribute, appContextAttr)))

            context['app'] = appContext

            # create returning xml matching app tag
            appOut = outDoc.createElement('app')
            appOut.setAttribute('appid', appContext['appid'])

            if appContext['appid'] in self.validAppIds:
                for appChildElement in appElement.childNodes:
                    if appChildElement.nodeType == Node.ELEMENT_NODE:
                        if appChildElement.nodeName == 'o:event': # process event tags
                            eventAttr = ['eventtype', 'eventresult', 'errorcode', 'extracode1', 'previousversion']
                            eventDict = dict(zip(eventAttr, map(appChildElement.getAttribute, eventAttr)))
                            self.processEvent(eventDict, context)

                            # add event response XML element
                            eventElementOut = outDoc.createElement('event')
                            eventElementOut.setAttribute('status', 'ok')
                            appOut.appendChild(eventElementOut)
                        elif appChildElement.nodeName == 'o:updatecheck': # process updatecheck tags
                            updateElementOut = outDoc.createElement('updatecheck')

                            if appContext['appid'] == self.bitpopAppId:
                                infoDict = loadJsonAndCheckIfLatestKeyExists(Config.bitpopUpdateInfoFile)
                                if infoDict['latestExists'] and (context['app']['version'] == '' or versionCompare(context['app']['version'], infoDict['jsonData']['latest']) == -1):
                                    updateInfo = infoDict['jsonData']
                                    hashError = False
                                    hash = ''
                                    if context['app']['version'] in updateInfo['delta']:
                                        updatePath = getPathToUpdate(updateInfo['latest'], context['app']['version'])
                                        updateUrl = getUpdateURL(updateInfo['latest'], context['app']['version'])
                                        try:
                                            i = updateInfo['delta'].index(context['app']['version'])
                                            hash = updateInfo['deltaHash'][i]
                                        except:
                                            hashError = True
                                    else:
                                        updatePath = getPathToUpdate(updateInfo['latest'])
                                        updateUrl = getUpdateURL(updateInfo['latest'])
                                        try:
                                            hash = updateInfo['latestHash']
                                        except:
                                            hashError = True
                                    if hashError:
                                        updateElementOut.setAttribute('status', 'error-hash')
                                    if not hashError and os.path.exists(updatePath):
                                        updateElementOut.setAttribute('Version', updateInfo['latest'])
                                        if context['app']['version']:
                                            updateElementOut.setAttribute('arguments', '--do-not-launch-chrome')
                                        else:
                                            updateElementOut.setAttribute('arguments', '')
                                        updateElementOut.setAttribute('codebase', updateUrl)
                                        updateElementOut.setAttribute('hash', hash)
                                        updateElementOut.setAttribute('needsadmin', 'false')
                                        updateElementOut.setAttribute('onsuccess', 'exitsilentlyonlaunchcmd')
                                        updateElementOut.setAttribute('size', str(os.path.getsize(updatePath)))
                                        updateElementOut.setAttribute('status', 'ok')
                                else:
                                    updateElementOut.setAttribute('status', 'noupdate')
                            else:
                                updateElementOut.setAttribute('status', 'noupdate')
                            appOut.appendChild(updateElementOut)
                        elif appChildElement.nodeName == 'o:ping': # process ping tags
                            # TODO: add processing of ping attributes for collecting usage data
                            pingElementOut = outDoc.createElement('ping')
                            pingElementOut.setAttribute('status', 'ok')
                            appOut.appendChild(pingElementOut)
                        elif appChildElement.nodeName == 'o:data': # process data tags
                            dataElementOut = outDoc.createElement('data')
                            # TODO: learn why is this data element needed
                            # say there's no data this time
                            dataElementOut.setAttribute('status', 'error-nodata')
                            appOut.appendChild(dataElementOut)
                        else: # unknown element
                            unknownElementOut = outDoc.createElement('unknown')
                            unknownElementOut.setAttribute('status', 'error')
                            appOut.appendChild(unknownElementOut)

                appOut.setAttribute('status', 'ok')
            else: # unknown app id
                appOut.setAttribute('status', 'error-unknownApplication')

            # append our app response to resulting XML
            outDoc.documentElement.appendChild(appOut)

        #log.msg('\nINPUT: ----------\n%s\n\nOUTPUT: ---------\n%s' % (doc.toprettyxml(encoding='utf-8'), outDoc.toprettyxml(encoding='utf-8')))
        return outDoc.toprettyxml(encoding='utf-8')
    def processEvent(self, event, context):
        return