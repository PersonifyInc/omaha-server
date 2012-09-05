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
from util import *
import os
from config import Config

class SwitchResource(resource.Resource):
    isLeaf = True
    pathFromRoot = '/service/admin/switch'

    def render_GET(self, request):
        if request.args.has_key('confirm') and request.args['confirm'][0] == 'y':
            try:
                if os.path.exists(Config.bitpopUpdateInfoFile):
                    os.remove(Config.bitpopUpdateInfoFile)
                os.rename(Config.bitpopNewUpdateInfoFile, Config.bitpopUpdateInfoFile)
            except:
                request.setResponseCode(500)
                return "Critical error. Consider manually updating config files."
            
            return """<!doctype html>
<html>
<head>
    <meta http-equiv="refresh" content="5;url=/service/admin">
    <title>House of Life Update Manager</title>
</head>
<body>
<p>Everything was fine.</p>
</body>
</html>"""

        return """<!doctype html>
<html>
<head>
    <title>House of Life Update Manager</title>
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js"></script>
    <script type="text/javascript">
        $(function () {{
            if (window.confirm('Are you sure you have uploaded' +
                               ' all files and want to switch' +
                               ' to new version?')) {{
                document.location.href = '{0}?confirm=y';
            }}
            else {{
                document.location.href = '/service/admin';
            }}
        }});
    </script>
<body>
</body>
</html>""".format(self.pathFromRoot)