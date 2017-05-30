# upload *.csv.gz files in a folder (recursively)
# 2017.05.27 - Szoke Sandor

import os
import requests
import ConfigParser

configfile = 'etc/koteslista_letolto.conf' 
config = ConfigParser.ConfigParser()
if not os.path.isfile(configfile):
  cfgfile = open(configfile, 'w')
  config.add_section('server')
  config.set('server', 'upload_url', 'http://localhost/tozsde/upload.php')
  config.write(cfgfile)
  cfgfile.close()

config.read(configfile)
url = config.get('server', 'upload_url', 'http://localhost/tozsde/upload.php')

for dirname, subdirs, files in os.walk("koteslistak"):
  for file in files:
    if (".csv.gz" or ".CSV.GZ") in file:  
      sourcefile = os.path.join(dirname, file)
      files = {'userfile': open(sourcefile, 'rb')}
      r = requests.post(url, files=files)
      print sourcefile,"-> ",r.text
