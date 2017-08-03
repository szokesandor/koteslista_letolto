#!/usr/bin/python
# -*- coding: utf-8 -*-
######
# upload *.csv.gz files in a folder (recursively)
# 2017.05.27 - Szoke Sandor
#
# javitasok:
# 2017.06.11 - Szoke Sandor
#            - beallitasok fajl betoltesenek hozzadasa
#
import os
import sys
import requests
import ConfigParser
import inspect

# use this if you want to include modules from a subfolder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"libs")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)
#print (sys.path)
from koteslista_beallitasok import beallitasokfajl_megnyitasa, beallitas_ertek

beallitasokfajl_megnyitasa('etc/koteslista_letolto.conf' )
url = beallitas_ertek('server', 'upload_url')

for dirname, subdirs, files in os.walk("koteslistak"):
  for file in files:
    if (".csv.gz" or ".CSV.GZ") in file:  
      sourcefile = os.path.join(dirname, file)
      files = {'userfile': open(sourcefile, 'rb')}
      r = requests.post(url, files=files)
      print sourcefile,"-> ",r.text
