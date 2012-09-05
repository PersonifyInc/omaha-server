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

import os, re, json
from twisted.web import resource
from config import Config
from util import *
#import hashlib, base64
from db_helper import DbHelper
#from M2Crypto import EVP, DSA, util
import os

class NewMacFullResource(resource.Resource):
    isLeaf = True
    pathFromRoot = '/service/admin/mac/new_full'

    def render_GET(self, request):
        output = """<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="chrome=1">

    <title>House of Life Update Manager</title>

    <!-- CSS: implied media="all" -->
    <!--<link rel="stylesheet" href="/css/style.css?v=2">-->
    <link rel="stylesheet" href="/css/upload.css?v=2">

    <script type="text/javascript">
        uploadPath = "{0}";
    </script>
    <script type="text/javascript" src="/js/upload.js"></script>""".format(self.pathFromRoot)
    
        output += """
    <!-- Load jQuery -->
    <script type="text/javascript" src="http://www.google.com/jsapi"></script>
    <script type="text/javascript">
    	google.load("jquery", "1");
    </script>

    <!-- Load TinyMCE -->
    <script type="text/javascript" src="/js/tiny_mce/jquery.tinymce.js"></script>
    <script type="text/javascript">
    	$().ready(function() {
    	    $('textarea.tinymce').tinymce({
    			// Location of TinyMCE script
    			script_url : '/js/tiny_mce/tiny_mce.js',

    			// General options
    			theme : "advanced",
    			plugins : "autolink,lists,pagebreak,style,layer,table,save,advhr,advimage,advlink,emotions,iespell,inlinepopups,insertdatetime,preview,media,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template,advlist",

    			// Theme options
    			theme_advanced_buttons1 : "save,newdocument,|,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,styleselect,formatselect,fontselect,fontsizeselect",
    			theme_advanced_buttons2 : "cut,copy,paste,pastetext,pasteword,|,search,replace,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,cleanup,help,code,|,insertdate,inserttime,preview,|,forecolor,backcolor",
    			theme_advanced_buttons3 : "tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,charmap,emotions,iespell,media,advhr,|,print,|,ltr,rtl,|,fullscreen",
    			theme_advanced_buttons4 : "insertlayer,moveforward,movebackward,absolute,|,styleprops,|,cite,abbr,acronym,del,ins,attribs,|,visualchars,nonbreaking,template,pagebreak",
    			theme_advanced_toolbar_location : "top",
    			theme_advanced_toolbar_align : "left",
    			theme_advanced_statusbar_location : "bottom",
    			theme_advanced_resizing : true,

    			// Example content CSS (should be your site CSS)
    			content_css : "/css/rel_notes.css" //,

    			// Drop lists for link/image/media/template dialogs
//    			template_external_list_url : "lists/template_list.js",
//    			external_link_list_url : "lists/link_list.js",
//    			external_image_list_url : "lists/image_list.js",
//    			media_external_list_url : "lists/media_list.js",

    			// Replace values for the template plugin
//    			template_replace_values : {
//    				username : "Some User",
//    				staffid : "991234"
//    			}
    		});
    	});
    </script>
    <!-- /TinyMCE -->
</head>
<body>
    <div id="container">
        <header>
        </header>
        <div id="main" role="main">"""

        output += """
            <h1>Upload BitPop mac new version</h1>
            
            <form id="form1" enctype="multipart/form-data" method="post" action="{0}">
              <div class="row">
                <label for="newVersion">Input New Version Number</label><br />
                <input type="text" name="newVersion" id="newVersion" />
              </div>
              <div class="row">
                <label for="release_notes_text">Release notes</label>
                <textarea class="tinymce" id="release_notes_text" name="releaseNotes"></textarea>
              </div>
              <div class="row">
                <label for="fileToUpload">Select a File to Upload</label><br />
                <input type="file" name="fileToUpload" id="fileToUpload" onchange="fileSelected();"/>
              </div>
              <div class="row">
              <input type="button" onclick="javascript:tinyMCE.activeEditor.save(); uploadFile();" value="Upload" />
              </div>
              <div id="fileInfo">
                <div id="fileName"></div>
                <div id="fileSize"></div>
                <div id="fileType"></div>
              </div>
              <div class="row"></div>
              <div id="progressIndicator">
                <div id="progressBar" class="floatLeft">
                </div>
                <div id="progressNumber" class="floatRight">&nbsp;</div>
                <div class="clear"></div>
                <div>
                  <div id="transferSpeedInfo" class="floatLeft" style="width: 80px;">&nbsp;</div>
                  <div id="timeRemainingInfo" class="floatLeft" style="margin-left: 10px;">&nbsp;</div>
                  <div id="transferBytesInfo" class="floatRight" style="text-align: right;">&nbsp;</div>
                  <div class="clear"></div>
                </div>
                <div id="uploadResponse"></div>
              </div>
              <p>
                <a href="/service/admin">Back to main page</a>
              </p>
            </form>""".format(self.pathFromRoot)

        output += """
        </div>
        <footer>
        </footer>
    </div>
</body>
</html>"""
        return output

    def render_POST(self, request):
        macdb = DbHelper()
        
        versionRegex = re.compile('^\d+\.\d+\.\d+\.\d+$')
        if not versionRegex.match(request.args['newVersion'][0]):
            request.setResponseCode(400) # Bad request
            return "Error: malformed version number."

        latest = macdb.fetch_latest()
        
        if latest != None and versionCompare(latest['version'], request.args['newVersion'][0]) != -1:
            request.setResponseCode(400) # Bad request
            return "Error: version number invalid. Supply version number greater than old version."
        
        newRecord = {};
        newRecord['version'] = request.args['newVersion'][0]
        newRecord['dmg_path'] = os.path.join(Config.bitpopDirectory, 'mac', 
                                                'BitPop-' + newRecord['version'] + '.dmg')
        newRecord['dmg_size'] = str(len(request.args['fileToUpload'][0]))

        outDir = os.path.join(Config.bitpopDirectory, 'mac')
        if not os.path.exists(outDir):
            os.mkdir(outDir, 0755)
        elif not os.path.isdir(outDir):
            os.remove(outDir)
            os.mkdir(outDir, 0755)
        filename = newRecord['dmg_path']

        try:
            outputStream = open(filename, 'wb')
            try:
              outputStream.write(request.args['fileToUpload'][0])
            finally:
              outputStream.close()

#            sha = hashlib.new('sha1')
#            sha.update(request.args['fileToUpload'][0])
#            hash = base64.b64encode(sha.digest())
            
            os.system('openssl dgst -sha1 -binary < "{0}" | openssl dgst -dss1 -sign "dsa_priv.pem" | \
                       openssl enc -base64 > sig.txt'.format(filename))
            
            sig = open('sig.txt', 'r')
            try:
              tsig = sig.readline()
            finally:
              sig.close()
            
            # md = EVP.MessageDigest('sha1')
            # md.update(request.args['fileToUpload'][0])
            # digest = md.final()
            # 
            # dsa = DSA.load_key(Config.dsaPrivateKeyFile)
            # sig = dsa.sign_asn1(digest)
            newRecord['dsa_signature'] = tsig.strip('\n\r\t ')
            newRecord['rel_notes'] = request.args['releaseNotes'][0];
            
            macdb.insert(newRecord)
            
            activeStream = open(Config.macActiveVersionFile, 'w')
            try:
              activeStream.write(newRecord['version'] + "\n")
            finally:
              activeStream.close()
        except IOError:
            request.setResponseCode(500) # Internal server error
            return "Error: Internal Server Error. Failed to do some file operation."

        macdb.cleanup()

        return "OK. File was successfully uploaded to server."
