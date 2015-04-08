import cherrypy
PROJECT_HOME='/home/g.ivanov/coding/blamer'
import sys
sys.path.append(PROJECT_HOME)
from jinja2 import Environment, BaseLoader, FileSystemLoader
import sqlite3
import spc_ask_utils
import re

class HelloWorld(object):
  def __init__(self):
    self.env = Environment(loader=FileSystemLoader(PROJECT_HOME + "/templates"))
    conn = sqlite3.connect(PROJECT_HOME+'example.db')
    c = conn.cursor()
    c.execute('''
      CREATE TABLE  IF NOT EXISTS tdi_report
      (id INTEGER PRIMARY KEY ASC, experiment_id INTEGER, dump_id INTEGER, url TEXT NOT NULL)
      ''')
  
  @cherrypy.expose
  def index(self):
    #return "Hello SPC world!"
    template = self.env.get_template('index.html')
    return template.render()

  @cherrypy.expose
  def ask_spc(self, query="", expected="", host_port="spell-idx:10214"):
    spc_ans = ""
    spc_data={}
    if query != "":
      #do ask spellchecker
      m = re.match(r"^(.*):([1-9][0-9]*)$", host_port)
      if m:
        spc_ans = spc_ask_utils.ask_spc({"q": query, "expected": expected, "wnf_tag": "1", "wnf_report": "1"}, m.group(1), int(m.group(2)));
        spc_data = spc_ask_utils.parse_spc_ans(spc_ans)
      else:
        spc_ans = "wrong host_port: [%s]"%(host_port)

    template = self.env.get_template('ask_spc.html')
    return template.render(query=query, expected = expected, spc_ans = spc_ans, spc_data = spc_data, host_port=host_port)
 
  @cherrypy.expose
  def load_tdi_form(self):
    template = self.env.get_template('load_tdi_form.html')
    return template.render()
  
  @cherrypy.expose
  def load_tdi(self, url, host_port_1, host_port_2):
    raise cherrypy.HTTPRedirect('list_tdi')

  @cherrypy.expose
  def list_tdi(self):
    conn = sqlite3.connect(PROJECT_HOME+'example.db')
    c = conn.cursor()
    c.execute('''
      SELECT id, url from tdi_report
      ''')
    template = self.env.get_template('list_tdi.html')
    return template.render(records=[1,2,3,4,5])


if __name__ == '__main__':
  cherrypy.config.update({
    'server.socket_port': 8080,
    'tools.proxy.on': True,
    'tools.proxy.base': 'http://127.0.0.1:8080'
  })
  cherrypy.quickstart(HelloWorld())

