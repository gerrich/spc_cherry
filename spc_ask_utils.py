#!/usr/bin/env python
# -*- coding: utf8 -*-
import urllib
import socket
import re
import sys
import codecs

def ask_spc(map, host, port, use_utf8 = True):
  utf_flag = ''
  if use_utf8:
    utf_flag = '&utf8=1'

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect((host, port))
  packet = ''
  for key,value in map.iteritems():
    packet = '%s%s=%s&'%(packet, key, urllib.quote(value.encode('utf8')))
  packet = packet + utf_flag + "\n\n\r"

  if use_utf8:
    packet = packet.encode('utf8')
  else:
    packet = packet.encode('cp1251')

  bytest_sent = sock.send(packet)

  child_output = ''
  data = sock.recv(1024)
  while len(data):
    child_output += data
    data = sock.recv(1024)
  sock.close()

  if use_utf8:
    child_output = child_output.decode('utf8')
  else:
    child_output = child_output.decode('cp1251')


  ans =  child_output.rstrip('\r\n\t ')
  return ans
  #return re.sub('\s+', ' ', ans)

def read_cdata_key(src, dst, key, key_out = None):
  if key_out == None:
    key_out = key
  m = re.search(r'<%s><!\[CDATA\[(.*?)\]\]></%s>'%(key,key), src)
  if m:
    dst[key_out] = m.group(1)
  
def read_key(src, dst, key, key_out = None):
  if key_out == None:
    key_out = key
  m = re.compile(r'<%s>(.*?)</%s>'%(key,key),re.DOTALL).search(src)
  if m:
    dst[key_out] = m.group(1)
  
def parse_spc_ans(src):
  data = {}

  read_cdata_key(src, data, 'CHK_Q', 'q') 
  read_key(src, data, 'CHK_HL_Q', 'html') 
  read_cdata_key(src, data, 'str', 'spcq') 
  read_cdata_key(src, data, 'html', 'hl') 
  read_cdata_key(src, data, 'orig', 'hl_orig') 

  data['verdict'] = 'none'
  if data.has_key('spcq') and data['spcq'] != "":
    if re.search(r'<reply auto="false">', src):
      data['verdict'] = "sugg"
    elif re.search(r'<reply auto="true">', src):
      data['verdict'] = "auto"
    else:
      data['verdict'] = "ERROR"

  read_key(src, data, 'FIX_TAGS') 
  read_key(src, data, 'ITERATION_COUNT') 
  
  read_key(src, data, 'wnf_tag') 
  read_key(src, data, 'wnf_report') 

  return data
