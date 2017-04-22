# gzip csv files in a folder (recursively)
# 2017.04.23 - Szoke Sandor

import os
import gzip
import shutil

for dirname, subdirs, files in os.walk("koteslistak"):
  for file in files:
    if (".csv" or ".CSV") in file:  
      sourcefile = os.path.join(dirname, file)
      destinationfile = sourcefile + ".gz"
      with open(sourcefile, 'rb') as f_in, gzip.open(destinationfile, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
      print "gzipped: " + destinationfile
