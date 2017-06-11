# import *.csv.gz files on server (get file list&iterate)
# 2017.06.05 - Szoke Sandor
#
# javitasok:
# 2017.06.11 - Szoke Sandor
#            - beallitasok fajl betoltesenek hozzadasa

import os
import requests
import ConfigParser
import json
import inspect

# use this if you want to include modules from a subfolder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"libs")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)
#print (sys.path)
from koteslista_beallitasok import beallitasokfajl_megnyitasa, beallitas_ertek

beallitasokfajl_megnyitasa('etc/koteslista_letolto.conf' )
url_list = beallitas_ertek('server', 'list_url')
url_import = beallitas_ertek('server', 'import_url')

r = requests.get(url_list)
j = r.json()
for file in j:
  payload = {'f': file["checksum"]}
  r = requests.get(url_import, params=payload)
#  print "-> ",file["index"],":", file["name"], "checksum:", file["checksum"] 
  print "-> ",r.text
