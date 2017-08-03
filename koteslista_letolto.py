#!/usr/bin/python
# -*- coding: utf-8 -*-
######
# koteslista letolto portfoli.hu-rol
# url: http://www.portfolio.hu/tozsde/koteslista-hist.tdp
# 2017.01.18 - Szoke Sandor <mail@szokesandor.hu>
#
# javitasok:
# 2017.08.03 - Szőke Sándor
#            - betű kódolás, hozzáadása
#            - urllib3 naplózás csökkentése 
# 2017.08.02 - Szoke Sandor
#            - naplozas hozzaadasa
#            - importalas hozzaadasa
# 2017.06.15 - Szoke Sandor
#            - for hiba javitasa 
#            - autoupload beallitas ertek kezelese, valamint autoimport beallitas hozzadasa
# 2017.06.11 - Szoke Sandor
#            - beallitasok fajl betoltesenek hozzadasa
# 2017.05.27 - Szoke Sandor
#            - letoltott fajl feltoltese azonnal szerverre
# 2017.04.23 - Szoke Sandor
#            - a letoltott csv fajlokat gzip-el tomoritve menti le 
# 2017.04.01 - Szoke Sandor
#            - print szintakszis javitasa
# 2017.03.31 - Szoke Sandor
#            - timestamp most mar oraallitas utan is helyes lesz 
# 2017.03.23 - Szoke Sandor
#            - bealitasok kulon mappaba mozgatasa
# 2017.03.19 - Szoke Sandor
#            - letrehozza a mappat a koteslistahoz
#
# Mukodes:
# - letrehoz egy tombot az elozo 7 nap datumabol (mind kell mert lehet, hogy a hetvege munkanap volt)
# - betolti az elozo letoltott datumokat
# - betolti az elteres file-t (munkanapathelyezesek miatt lehet erdekes)
# - osszefesuli az elozo harmat
# - a maradekot letolti
# - frissiti letoltott fajlok listajat es elmenti a listat
# - feltolti a letoltott fajlokat a megadott szerverre
#
#
# letoltesi link:
# href="http://www.portfolio.hu/tozsde/koteslista-hist.tdp?datum=1489446000&amp;xls=1"
# 
from __future__ import print_function

import urllib
import urllib2
#from urllib2 import Request, urlopen, URLError, HTTPError
from urllib2 import URLError

import os
import sys
import re
import pytz
from datetime import datetime, date, time, timedelta
from time import sleep
import gzip
import StringIO
import requests
import ConfigParser
import inspect
import logging

# use this if you want to include modules from a subfolder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"libs")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)
#print (sys.path)
from koteslista_beallitasok import beallitasokfajl_megnyitasa, beallitas_ertek

LogFolder = "./logs/"

beallitasokfajl_megnyitasa('etc/koteslista_letolto.conf' )
url = beallitas_ertek('server', 'upload_url')
autoupload = beallitas_ertek('server', 'autoupload')

autoimport = beallitas_ertek('server', 'autoimport')
url_list   = beallitas_ertek('server', 'list_url')
url_import = beallitas_ertek('server', 'import_url')

#print ("URL: ",url)
#sys.exit(-1)
#----
#----
# fajl letoltese adott mappaba
# status:
#   0 - minden rendben
#   1 - letoltes sikertelen
#--------------------------------------------------
def FileDownload(dt,mappa):
  exitcode = 0
  mappa = './' + mappa
  # mappa letezes ellenorzese
  if not os.path.exists(str(mappa) + '/.'):
    os.makedirs(mappa)
  #print ("down:" + str(dt) )
  #url = "http://www.portfolio.hu/tozsde/koteslista-hist.tdp?datum=1489446000&xls=1"
  #url = "http://localhost/download/file1.php"
  url = "http://www.portfolio.hu/tozsde/koteslista-hist.tdp"
  user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
  request_headers = {'User-Agent': user_agent, 
                     'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                     "Accept-Language": 'hu-HU,hu;q=0.8,en-US;q=0.5,en;q=0.3'}
  values = {'xls': '1',
            'datum': Timestamp(dt) }
  data = urllib.urlencode(values)

  req = urllib2.Request(url+"?"+ data,headers=request_headers)
  try:
    httpobj = urllib2.urlopen(req)
    headers = httpobj.info()
    content = httpobj.read()
  except URLError as e:
    if hasattr(e, 'reason'):
        exitcode = 1
        logging.error('Szerver elerese sikeretelen. Oka: ' + str(e.reason) + " @ " + dt.strftime('%Y-%m-%d') + " " +url+"?"+ data)
#        print ('We failed to reach a server. Reason: ', e.reason)
        return exitcode
    elif hasattr(e, 'code'):
        exitcode = 1
        logging.error('A szerver nem tudja teljesiteni a kerest. Hibakod: ' + str(e.code) + " @ " + dt.strftime('%Y-%m-%d') + " " + url+"?"+ data)
#        print ('The server couldn\'t fulfill the request. Error code: ', e.code)
        return exitcode
  else:
    exitcode = 0
#  print(headers)
#  print(headers.getheaders("Content-Disposition"))
  content_disposition=headers.getheaders("Content-Disposition")
  if (len(content_disposition) > 0):
    filename = re.findall(r'"([^"]*)"',headers.getheaders("Content-Disposition")[0])
    #    print("filename: " + filename[0])
    gzipr = StringIO.StringIO()
    tmpf = gzip.GzipFile(filename=filename[0], mode='wb', fileobj=gzipr,)
    tmpf.write(content)
    tmpf.close()
    gzipr.seek(0)
    f = open(mappa + "/" + filename[0] + ".gz", 'wb')
    f.write(gzipr.read())
    f.close()
    logging.info("Letoltve: " + filename[0]+".gz")
    if (autoupload == "yes"):
      Feltoltes(mappa + "/" + filename[0] + ".gz")
  else:
    logging.info("Letoltesre nem elerheto" + dt.strftime('%Y-%m-%d'))
#    print ("Letoltesre nem elerheto: " + dt.strftime('%Y-%m-%d'))
    exitcode = 1
  return exitcode
#--------------------------------------------------
#----
# fajl feltoltese szerverre
def Feltoltes(fajl):
  files = {'userfile': open(fajl, 'rb')}
  r = requests.post(url, files=files)
  logging.info("Feltoltve: " + r.text)
#  print (r.text)
#--------------------------------------------------
#----
# visszaadja a Unix Timestamp-et szovegkent
# 
def Timestamp(dt):
  dt = datetime.combine(dt,time(0,0))
  dt=pytz.timezone('Europe/Budapest').localize(dt)
#  print ("toUnix:" + str(dt))
  epoch = pytz.utc.localize(datetime(1970,1,1))
  timestamp = (dt - epoch).total_seconds()
  return int(timestamp)
#----
# az elso listarol leszedi azokat akik rajta vannak a masodikon
def LetolteniDatumok(modositottdates,letoltve):
  ujlista=[]
  for datum in modositottdates:
    if (str(datum) in letoltve):
        pass
    else :
      ujlista.append(datum)
  return ujlista
#----
def LetoltottNapokBetoltese(letoltottfajl):
  datumlista=[]
  if os.path.exists(str(letoltottfajl)):
    f = open(letoltottfajl, 'r')
    file = f.read()  # python will convert \n to os.linesep
    f.close()

    lines = file.splitlines()
    for line in lines:
      line = line.strip()                 
      datumlista.append(line)
  return datumlista
#----
# a ket listat modositja, hogy az aktualisban a munkanap athelyezesek is benne legyenek
# jelenleg csak a munkaszuneti napokat ertelmezi
def osszefesul(aktualis, modosito):
  ujlista=[]
# 2017-ben nincs szombati munkanap!  
#  elsonap = aktualis[0]
#  for datum in aktualis:
#    if (elsonap > datum):
#      elsonap = datum
#  print "2",elsonap, "fesules start"
#  print modosito
  for datum in aktualis:
    if (str(datum) in modosito.keys()):
      allapot=modosito[str(datum)]
      if (allapot == "-"):
#        print ("torolve:"+ str(datum)+ str(allapot))
        logging.debug("Torolve: "+ str(datum)+ str(allapot))
        pass
    else :
      ujlista.append(datum)
  return ujlista
#----
def MunkanapAthelyezesBetoltese(fajlnev):
  # betolti a teljes fajlt
  f = open(fajlnev, 'r')
  file = f.read()  # python will convert \n to os.linesep
  f.close()
  #print file
  datumlista={}

  #---
  # megszuri a megjegyzeseket, ures sorokat
  lines = file.splitlines()             # split to lines
  for line in lines:                    # iterate via lines
    line = line.strip()                 # sorhossz adatra = 12!
    if (line.startswith("#")):          # megjegyzes kihagyasa
      pass
    elif(":" in line):                  # ha van benne kettospont
      name = line.split(":")            # split the parameter from value
      name[0] = name[0].strip()
      name[1] = name[1].strip()
      datumlista[name[0]]=name[1]
  return datumlista
#----
# az elozo napok generalasa
def ElozoNapok(elozonapokszama):
#  t = time(0,0,0)
  dstart = date.today() - timedelta(days=elozonapokszama)
  datumlista = []
  for day in range(elozonapokszama):
    d = dstart + timedelta(days=day)
    if (d.isoweekday() < 6):  # csak a munkanapok kellenek
      datumlista.append(d)
  return datumlista
#------------------------------------------------------------------------------------
# kiirja az elozo 7 nap datumat

if __name__ == '__main__' :
# naplozas beallitasa
  try:
    if not os.path.exists(LogFolder):
      raise Exception('ERROR: Folder is not exists')
    if os.path.isfile(LogFolder):
      raise Exception('ERROR: Folder to store logs is a file!')
  except Exception as e:
    print(e)
    sys.exit(-1)
  logFile = "koteslista_letolto_@_" + datetime.now().strftime('%Y%m%d_%H%M%S') + ".log"
  logging.basicConfig(filename=os.path.join(LogFolder, logFile),format='%(asctime)s %(message)s', level=logging.INFO)
#  logging.getLogger('').setLevel(logging.DEBUG) ## only if needed
  logging.getLogger("requests").setLevel(logging.WARNING)
  logging.getLogger("urllib3").setLevel(logging.WARNING)
  console = logging.StreamHandler()
  console.setLevel(logging.INFO)
  formatter = logging.Formatter('%(message)s')
  console.setFormatter(formatter)
  logging.getLogger('').addHandler(console)
###
  lista = ElozoNapok(6)
  date_strings = [dt.strftime('%Y-%m-%d') for dt in lista]
  logging.debug("Elozo napok: "+";".join(date_strings))
#  print("Elozo napok:")
#  for i in range(len(lista)):
#    print (lista[i])

# munkanapathelyezesek fajl
  MODFILE="./etc/modfile.txt"
  moddates = MunkanapAthelyezesBetoltese(MODFILE)
  modositottdates=osszefesul(lista,moddates)
#  print "\nModositott napok:"
#  for i in range(len(modositottdates)):
#    print modositottdates[i]
  
# utoljara letoltott datumok listaja
  LETOLTOTT="./etc/letoltott.txt"
  letoltve = LetoltottNapokBetoltese(LETOLTOTT)
  logging.info("Letoltve:    "+";".join(letoltve[-5:]))
#  print ("\nLetoltve:")
# csak az utolso 5 nap listazasa
#  for i in range(-5,0):
#    print (letoltve[i])

  letolteni = LetolteniDatumok(modositottdates,letoltve)
  date_strings = [dt.strftime('%Y-%m-%d') for dt in letolteni]
  logging.info("Letoltendok: "+";".join(date_strings))
#  print ("\nLetolteni: ")
#  for i in range(len(letolteni)):
#    print (letolteni[i])

  # fajlok letoltese egyesevel
  MAPPA="koteslistak"
  ilen = len(letolteni)
  for i in range(len(letolteni)):
    status = FileDownload(letolteni[i],MAPPA)
    # 0 - ok
    # 1 - error
    if (status == 0):
      # hozzadas letoltve listahoz
      letoltve.append(letolteni[i])
    if ((ilen > 1) and (i < (ilen-1))):
      sleep(10)
  # letoltott datumok fajl kiirasa
  f = open(LETOLTOTT, 'w')
  for item in letoltve:
    f.write("%s\n" % item)
  f.close()
  if (autoimport == "yes"):
#      Importalas("Letoltve: " + mappa + "/" + filename[0] + ".gz")
    r = requests.get(url_list)
    j = r.json()
    file_strings = [i["name"] for i in j]
    logging.info("Importalando fajlok: "+";".join(file_strings))
    for file in j:
      payload = {'f': file["checksum"]}
      r = requests.get(url_import, params=payload)
#      print "-> ",file["index"],":", file["name"], "checksum:", file["checksum"] 
#      print "-> ",r.text
      logging.info("-> " + r.text)
