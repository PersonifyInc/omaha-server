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

import os
if os.name == 'posix':
  import pwd

class Config:
    isProduction = False
  
    # DB config
    dbTestHost = 'localhost'
    dbTestUser = 'root'
    dbTestPwd = ''
    dbTestDbName = 'omaha'
    
    dbProdHost = 'localhost'
    dbProdUser = 'toolsbit_omaha'
    dbProdPwd = ''
    dbProdDbName = 'toolsbit_omaha'

    if isProduction:
      dbHost = dbProdHost
      dbUser = dbProdUser
      dbPwd = dbProdPwd
      dbDbName = dbProdDbName
    else:
      dbHost = dbTestHost
      dbUser = dbTestUser
      dbPwd = dbTestPwd
      dbDbName = dbTestDbName
  
    # SSL config
    useCertificateChain = False
    certificateChainFile = 'cert/gd_bundle.crt'
    certificateFile = 'cert/ca.cer'
    privateKeyFile = 'cert/ca.key'
    
    # Network config
    httpPort = 8081
    httpsPort = 8083
    if isProduction:
      domainName = 'tools.bitpop.com'
    else:
      domainName = 'localhost'
      
    secureDomain = 'https://' + domainName
    insecureDomain = 'http://' + domainName
    
    # Application config
    bitpopDirectory = 'bitpop'
    installerName = 'NuvixaChatInstall.exe'
    bitpopUpdateInfoFile = 'bitpop.json'
    bitpopNewUpdateInfoFile = 'bitpop_new.json'
    macActiveVersionFile = 'mac_active.txt'
    dsaPrivateKeyFile = 'dsa_priv.pem'
  
    userName = 'nobody'
    uid = pwd.getpwnam(userName).pw_uid if os.name == 'posix' else 0
    gid = pwd.getpwnam(userName).pw_gid if os.name == 'posix' else 0