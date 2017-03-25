# koteslista letolto portfoli.hu-rol
# url: http://www.portfolio.hu/tozsde/koteslista-hist.tdp
# 2017.01.18 - Szoke Sandor
#
# Mukodes:
# - letrehoz egy tombot az elozo 7 nap datumabol (mind kell mert lehet, hogy a hetvege munkanap volt)
# - betolti az elozo letoltott datumokat
# - betolti az leteres file-t
# - osszfesuli az elozo harmat
# - a maradekot letolti
# - frissiti letoltott fajlok listajat es elmenti azt

# letoltesi link:
# href="http://www.portfolio.hu/tozsde/koteslista-hist.tdp?datum=1489446000&amp;xls=1"
# nehany adat:
# 
from __future__ import print_function

import urllib
import urllib2
#from urllib2 import Request, urlopen, URLError, HTTPError
from urllib2 import URLError

import os
import re
from datetime import datetime, date, time, timedelta
from time import sleep

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
        print ('We failed to reach a server. Reason: ', e.reason)
        return exitcode
    elif hasattr(e, 'code'):
        exitcode = 1
        print ('The server couldn\'t fulfill the request. Error code: ', e.code)
        return exitcode
  else:
    exitcode = 0
  #print(headers)
  #print(headers.getheaders("Content-Disposition"))
  content_disposition=headers.getheaders("Content-Disposition")
  if (len(content_disposition) > 0):
    filename = re.findall(r'"([^"]*)"',headers.getheaders("Content-Disposition")[0])
    #    print("filename: " + filename[0])
    with open(mappa + "/" + filename[0], 'wb') as f:
      print(content, file=f)
  else:
    print ("not available for download")
    exitcode = 1

#  with open('headers', 'w') as f:
#    print(headers, file=f)
#
  return exitcode
#--------------------------------------------------
#----
# visszaadja a Unix Timestamp-et szovegkent
# 
def Timestamp(dt):
#  dt = datetime(2017, 1, 14)
  dt = datetime.combine(dt,time(0,0))
  print ("toUnix:" + str(dt))
  print (str(type(dt)))
  dt = dt + timedelta(hours=-1)
  
  print (dt)
  timestamp = (dt - datetime(1970, 1, 1)).total_seconds()
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
        print ("torolve:"+ str(datum)+ str(allapot))
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

  lista = ElozoNapok(7)
  print("Elozo napok:")
  for i in range(len(lista)):
    print (lista[i])

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
  print ("\nLetoltve:")
  for i in range(len(letoltve)):
    print (letoltve[i])

  letolteni = LetolteniDatumok(modositottdates,letoltve)
  print ("\nLetolteni: ")
  for i in range(len(letolteni)):
    print (letolteni[i])

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
    if (ilen > 1):
      sleep(10)
  # letoltott adtumok fajl kiirasa
  f = open(LETOLTOTT, 'w')
  for item in letoltve:
    f.write("%s\n" % item)
  f.close()
       
   