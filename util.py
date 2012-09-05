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

import os, json
from config import Config

def getPathToUpdate(versionTo, versionFrom = None):
    res = '{0}/{1}'.format(Config.bitpopDirectory, versionTo)
    if versionFrom is None or versionFrom == '':
        return res + '/' + Config.installerName
    return res + '/' + versionFrom + '/' + Config.installerName

def getUpdateURL(versionTo, versionFrom = None):
    return Config.insecureDomain + '/' + getPathToUpdate(versionTo, versionFrom)

def getUpdateURLMac(dmg_path):
    return Config.insecureDomain + '/' + Config.bitpopDirectory + '/mac/' + dmg_path

def loadJsonAndCheckIfLatestKeyExists(filename):
    latestExists = True
    jsonInfo = None
    jsonFile = None

    if os.path.exists(filename) and os.path.isfile(filename):
        try:
            jsonFile = open(filename, "r")
        except:
            latestExists = False
        if latestExists:
            try:
                jsonInfo = json.load(jsonFile)
            except:
                latestExists = False
            finally:
                jsonFile.close()

            if type(jsonInfo) != type({}) or not jsonInfo.has_key("latest"):
                latestExists = False
    else:
        latestExists = False
    return { 'jsonData': jsonInfo, 'latestExists': latestExists }

def versionCompare(v1, v2):
    v1s = v1.split('.')
    v2s = v2.split('.')
    for x, y in zip(v1s, v2s):
        if int(x) < int(y): return -1;
        if int(x) > int(y): return 1;
    return 0
