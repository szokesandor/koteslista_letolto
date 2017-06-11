# kotelista_letolto beallitasok fajl kezelese
# 2017.06.11 - Szoke Sandor

import sys
import os
import requests
import ConfigParser
#import inspect

configfile = ''
config = None

def beallitasokfajl_megnyitasa(beallitasfajl):
  global configfile
  global config
#  print "Root:", beallitas
#  caller = inspect.stack()[1] 
#  print "caller: ",caller[1]
  configfile = beallitasfajl
  if not os.path.isfile(beallitasfajl):
    beallitasokfajl_letrehozasa()
  if config == None:
      config = ConfigParser.ConfigParser()
  config.read(beallitasfajl)

def beallitasokfajl_letrehozasa():
  global configfile
  global config
  cfgfile = open(configfile, 'w')
  config.add_section('server')
  config.set('server', 'upload_url', 'http://localhost/tozsde/upload.php')
  config.set('server', 'list_url', 'http://localhost/tozsde/csv_lister.php')
  config.set('server', 'import_url', 'http://localhost/tozsde/csv_gz_import.php')
  config.set('server', 'autoupload', 'yes') # fajlok feltoltese
  config.set('server', 'autoimport', 'yes') # fajlok importalasa feltolteskor
  config.write(cfgfile)
  cfgfile.close()

def beallitas_ertek(szekcio, kulcs):
  ertek = config.get(szekcio, kulcs)
  return ertek
