from twisted.web import resource
from db_helper import DbHelper
import re, cgi

class MacEditResource(resource.Resource):
  pathFromRoot = '/service/admin/mac/edit'
  isLeaf = True
  
  def render_GET(self, request):
    tr = re.compile('.*/(\d*)$')
    m = re.match(tr, request.path)
    if len(m.groups()) == 0:
      request.setResponseCode(400) # Bad request
      return "Error: Bad request."
    update_id = m.groups()[0]
    
    macdb = DbHelper()
    upd = macdb.fetch_by_id(int(update_id))
    macdb.cleanup()
    
    if upd == None:
      request.setResponseCode(404) # Not found
      return "Error: Record with such id not found."
    
    output = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="chrome=1">

<title>House of Life Update Manager</title>

<!-- CSS: implied media="all" -->
<link rel="stylesheet" href="/css/style.css?v=2">

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
</head>"""
    output += """
<body>
<div id="container">
    <header>
      <h1>Edit Release Notes for Mac version</h1>
      <p>Copyright &copy; 2011, House of Life Property ltd. All rights reserved.<br />
         Copyright &copy; 2011, Crystalnix &lt;vgachkaylo@crystalnix.com&gt;</p>
    </header>
    <div id="main" role="main">
      <form method="post">
        <label for="release_notes_text">Release Notes</label>
        <textarea class="tinymce" style="height: 400px" name="rel_notes" id="release_notes_text">{0}</textarea>
        <input type="hidden" name="rec_id" value="{1}" />
        <input type="submit" value="Submit" />
      </form>
    </div>
    <footer>
    </footer>
</body>
</html>
""".format(cgi.escape(upd['rel_notes']), str(upd['id']))
    
    return output
  
  
  def render_POST(self, request):
    if not 'rel_notes' in request.args or not 'rec_id' in request.args:
      request.setResponseCode(400) # Bad request
      return "Error: Bad request."
    
    macdb = DbHelper()
    upd = macdb.fetch_by_id(int(request.args['rec_id'][0]))
    
    if upd == None:
      request.setResponseCode(404) # Bad request
      return "Error: Not found."
    
    upd['rel_notes'] = request.args['rel_notes'][0];
    macdb.update(upd)
    
    macdb.cleanup()
    
    return """<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="refresh" content="3;url=/service/admin">
  <title>Release notes changed</title>
</head>
<body>
  <h1>Success</h1>
  <p>Release notes changed successfully. You will be redirected in 3 seconds.</p>
</body>
</html>
"""
