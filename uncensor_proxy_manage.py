from twisted.web import resource
from db_helper import DbHelper
from config import Config
import urllib
import pycountry

class UncensorProxyManageResource(resource.Resource):
  isLeaf = True
  pathFromRoot = '/service/admin/uncensorp'

  def render_GET(self, request):
    macdb = DbHelper()
    res = macdb.uncensorp_fetch_all()
    msg = request.args['msg'][0] if 'msg' in request.args else ''
    
    output = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="chrome=1">

<title>House of Life Update Manager</title>

<!-- CSS: implied media="all" -->
<link rel="stylesheet" href="/css/style.css?v=2">
<link rel="stylesheet" href="/css/uncensor_domains.css">

<!-- Load jQuery -->
<script type="text/javascript" src="http://www.google.com/jsapi"></script>
<script type="text/javascript">
	google.load("jquery", "1");
</script>

<script type="text/javascript">
  function post_to_url(path, params, method) {
      method = method || "post"; // Set method to post by default, if not specified.

      // The rest of this code assumes you are not using a library.
      // It can be made less wordy if you use one.
      var form = document.createElement("form");
      form.setAttribute("method", method);
      form.setAttribute("action", path);

      for(var key in params) {
          var hiddenField = document.createElement("input");
          hiddenField.setAttribute("type", "hidden");
          hiddenField.setAttribute("name", key);
          hiddenField.setAttribute("value", params[key]);

          form.appendChild(hiddenField);
      }

      document.body.appendChild(form);
      form.submit();
  }

  $(function() {
    $('#countries').change(function() {
      if ($('#countries option:selected').val()) {
        $('#cur_country_icon').attr('src', '/img/gif-flags/' +
            $('#countries option:selected').val().toLowerCase() + '.gif');
        $('#cur_country_icon').show();
      }
    });
  });
</script>

<style type="text/css">
  #banner {"""
    
    if msg == "":
      output += """
    display:none;"""
    
    output += """
  }
</style>

</head>
<body>
<div id="container">
  <header>
    <h1>Uncensor Proxy domains</h1>
    <p>Copyright &copy; 2012, House of Life Property ltd. All rights reserved.<br />
       Copyright &copy; 2012, Crystalnix &lt;vgachkaylo@crystalnix.com&gt;</p>
  </header>
  <div id="main" role="main">
    <div id="banner">
      %s
    </div>

    <p>
      <a href="javascript:void(0)" onclick="javascript:$('#add_form').show(); return false;">Add domain pair</a>
    </p>
      
    <form id="add_form" style="display:none" method="post">
      <label for="countries">
        Country:
        <select id="countries" name="iso">
          <option value="">Choose from list...</option>""" % (msg)

    country_list = list(pycountry.countries)
    for country in country_list:
      output += '<option value="' + country.alpha2.encode('utf-8') + '">' + country.name.encode('utf-8') + '</option>'

    output += """
          </select>

          <img id="cur_country_icon" style="display:none" src="/img/gif-flags/us.gif" alt="flag" title="US" />
        </label>

        <label for="domain">
          Original domain:
          <input type="text" id="domain" name="domain" />
        </label>

        <input type="hidden" name="action" value="add" />
        <input type="Submit" value="Submit" />
      </form>
      
      <table id="domains">
        <thead>
          <tr><th>Country</th>
              <th>Blocked domain</th>
              <th>Actions</th>
          </tr>
        </thead>
        <tbody>"""
    if len(res) == 0:
      output += """
          <tr><td colspan="3" style="text-align: center">No domains in database</td></tr>"""
    
    ctr = 0
    prevCountry = ""
    for row in res:

      output += """
          <tr class="{5}">
            <td><img src="/img/gif-flags/{0}.gif" alt="{1}" /> {1}</td>
            <td>{2}</td>
            <td><a href="javascript:if (confirm('Do you really want to delete this record?')) 
                                      post_to_url('{3}', {{'id': '{4}', 'action':'delete'}})">Delete</a></td>
          </tr>""".format(row['iso'].lower(), pycountry.countries.get(alpha2=row['iso']).name,
                          row['domain'], self.pathFromRoot, str(row['id']),
                          'even-row' if ctr % 2 == 0 else 'odd-row')
      ctr += 1
          
    output += """
        </tbody>
      </table>
    </div>
    <footer>
    </footer>
</body>
</html>
"""
    macdb.cleanup()
    
    return output
    
  def render_POST(self, request):
    macdb = DbHelper()
    
    if not 'action' in request.args:
      request.setResponseCode(400)
      return 'Error 400. Bad request.'
    
    output = ""
    
    if request.args['action'][0] == 'delete':
      id_ = int(request.args['id'][0])
      rec = macdb.uncensorp_fetch_by_id(id_)
      request.setResponseCode(301)
      if rec != None:
        macdb.uncensorp_delete(id_)
        request.setHeader('Location', self.pathFromRoot + '?msg=' + urllib.quote_plus('Success. Record deleted.'))
      else:
        request.setHeader('Location', self.pathFromRoot + '?msg=' + urllib.quote_plus('Error. Record not found.'))
    elif request.args['action'][0] == 'add':
      if (not ('domain' in request.args)) or (not ('iso' in request.args)):
        request.setResponseCode(400)
        return 'Error 400. Bad request.'
      
      insertInfo = { 'domain': request.args['domain'][0], 'iso': request.args['iso'][0] }
      macdb.uncensorp_insert(insertInfo)
      request.setResponseCode(301)
      request.setHeader('Location', self.pathFromRoot + '?msg=' + urllib.quote_plus('Success. Record was added.'))
    else:
      request.setResponseCode(400)
      output = 'Error 400. Bad request.'
    
    macdb.cleanup()
    
    return output
