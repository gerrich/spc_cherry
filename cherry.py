# -*- coding: utf8 -*-

PROJECT_HOME='/home/g.ivanov/coding/blamer'
import sys
sys.path.append(PROJECT_HOME)
import cherrypy
import random
import string
import dircache
import os
from jinja2 import Environment, BaseLoader, FileSystemLoader
import gzip
import shingle
import subprocess

def decode_smart(data):
  for encoding in ['utf8','cp1251']:
    try:
      return data.decode(encoding), encoding
    except:
      pass
  return data, None

def look_shingles(records):
  base_path=PROJECT_HOME + "/shingles/000024.all.txt"
  for record in records:
    #entries =  subprocess.Popen(['echo', '1', '2', '3'], stdout=subprocess.PIPE).communicate()[0]
    entries =  subprocess.Popen(['look',record['value'], base_path], stdout=subprocess.PIPE).communicate()[0]
    tags=[]
    for entry in entries:
      fields= entry.split(' ')
      tags.append(fields[0])
    record['tags'] = tags

# Our CherryPy application
class Root(object):
  def __init__(self):
    self.env = Environment(loader=FileSystemLoader(PROJECT_HOME))
    self.runs_path = PROJECT_HOME + "/judges/000024/var/archive/runs/"

  @cherrypy.expose
  def index(self):
    return "hello world"

  @cherrypy.expose
  def generate(self):
    return ''.join(random.sample(string.hexdigits, 8))

  @cherrypy.expose
  def _list(self):
    items = dircache.listdir(PROJECT_HOME + '/judges/000024/var/archive/')
    return "items " + str(items)
  
  @cherrypy.expose
  def list(self):
    file_list=[]
    for root, dirs, files in os.walk(self.runs_path):
      for file in files:
        file_list.append(os.path.join(root, file))
        #if file.endswith(".txt"):
        #  print(os.path.join(root, file))
    template = self.env.get_template('list.html')
    return template.render(files=file_list)

  @cherrypy.expose
  def file(self, runid=""):
    id=int(runid)
    codes=list('0123456789ABCDEFGHIJKLMNOPQRTSTUVWXYZ')
    a2 = codes[(id >> 5)%32]
    a3 = codes[(id >> 10)%32]
    a4 = codes[(id >> 15)%32]
    path = self.runs_path + "%s/%s/%s/%06d"%(a4,a3,a2,id)

    data='UNDEFINED'
    fname=path
    try:
      f=open(path,'r')
      data=f.read()
      f.close()
    except:
      fname=path + '.gz'
      f=gzip.open(fname, 'rb')
      data=f.read()
      f.close()

    data,encoding = decode_smart(data)
    shingles = shingle.make_shingles(data.split("\n"))
    look_shingles(shingles)

    #return "[" + runid + "] %s/%s/%s"%(a4,a3,a2)
    template = self.env.get_template('data.html')
    return template.render(data = data, encoding=encoding, fname = fname, shingles = shingles)

cherrypy.config.update({'engine.autoreload.on': False})
cherrypy.server.unsubscribe()
cherrypy.engine.start()

application = cherrypy.tree.mount(Root())
