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

import sys
sys.path.append('.')

from encodings import hex_codec, base64_codec
from twisted.application import service, internet
from twisted.web import server, resource
from twisted.internet import ssl
from twisted.web.static import File
from chained_ssl import ChainedOpenSSLContextFactory
from update import UpdateXMLProcessor
from config import Config
from twisted.web.script import ResourceScriptWrapper
from twisted.web.guard import HTTPAuthSessionWrapper, DigestCredentialFactory
from twisted.cred.portal import Portal
from twisted.cred.checkers import FilePasswordDB
from auth import PublicHTMLRealm
import os
from mac_feed import MacFeedResource
from uncensor_out import UncensorOutResource
from uncensorp_out import UncensorPOutResource

class NoListingDir(File):
  def directoryListing(self):
    return resource.ForbiddenResource()

class LatestMacResource(resource.Resource):
  isLeaf = True

  def render_GET(self, request):
    try:
      f = open(Config.macActiveVersionFile, "r")
      vernum = f.readline().strip("\r\n\t ")
    except IOError:
      return resource.NoResource().render_GET(request)

    pathToFile = Config.bitpopDirectory + '/mac/BitPop-' + vernum + '.dmg'

    return File(pathToFile).render_GET(request)

if not os.path.exists(Config.bitpopDirectory):
    os.mkdir(Config.bitpopDirectory, 0755)
if not os.path.isdir(Config.bitpopDirectory):
    os.remove(Config.bitpopDirectory)
    os.mkdir(Config.bitpopDirectory, 0755)
    
root = resource.ForbiddenResource()
err = resource.ForbiddenResource()
root.putChild("service", err)
upd = UpdateXMLProcessor()
err.putChild("update2", upd)

portal = Portal(PublicHTMLRealm(), [FilePasswordDB('httpd.password')])
credentialFactory = DigestCredentialFactory("md5", "House of Life Updates")
admin = HTTPAuthSessionWrapper(portal, [credentialFactory])
err.putChild('admin', admin)

root.putChild('css', NoListingDir('css'))
root.putChild('js', NoListingDir('js'))
root.putChild('img', NoListingDir('img'))

insecureDomainResource = resource.ForbiddenResource()

bitpopDir = NoListingDir(Config.bitpopDirectory)

bitpopDir.putChild('BitPop.dmg', LatestMacResource())

bitpopDir.putChild('HouseOfLifeInstaller.application', \
  File('clickonce/HouseOfLifeInstaller.application', 'application/x-ms-application'))
bitpopDir.putChild('clickonce_bootstrap.exe.manifest', \
  File('clickonce/clickonce_bootstrap.exe.manifest', 'application/x-ms-manifest'))
bitpopDir.putChild('HouseOfLifeUpdateSetup.exe', \
  File('clickonce/bin/HouseOfLifeUpdateSetup.exe'))
bitpopDir.putChild('clickonce_bootstrap.exe',
  File('clickonce/bin/clickonce_bootstrap.exe'))

insecureDomainResource.putChild(Config.bitpopDirectory, bitpopDir)
insecErr = resource.ForbiddenResource()
insecureDomainResource.putChild("service", insecErr)
insecUpd = UpdateXMLProcessor()
insecErr.putChild("update2", insecUpd)
insecMacFeed = MacFeedResource()
insecErr.putChild('mac_feed', insecMacFeed)
uncen = UncensorOutResource()
insecErr.putChild("uncensor_domains", uncen)
uncenp = UncensorPOutResource()
insecErr.putChild("uncensorp_domains", uncenp)

httpSite = server.Site(insecureDomainResource)
httpsSite = server.Site(root)

if os.name == 'posix' and os.getuid() == 0:
  # run under user 'nobody'
  application = service.Application('House of Life Update Portal', uid=Config.uid, gid=Config.gid)
else:
  application = service.Application('House of Life Update Portal')

httpService = internet.TCPServer(Config.httpPort, httpSite, interface=Config.domainName)
httpsService = internet.SSLServer(Config.httpsPort, httpsSite,
                                      # Use custom factory for certificate chain
                                      ChainedOpenSSLContextFactory(
                                        privateKeyFileName=Config.privateKeyFile,
                                        certificateChainFileName=Config.certificateChainFile,
                                        certificateFileName=Config.certificateFile)
                                    if Config.useCertificateChain else
                                      # Use default factory for single certificate
                                      ssl.DefaultOpenSSLContextFactory(
                                        Config.privateKeyFile, Config.certificateFile),
                                  interface=Config.domainName)
httpService.setServiceParent(application)
httpsService.setServiceParent(application)

