# koteslista_letolto.py

## leírás
A http://portfolio.hu oldalon a koteslistak 1 hétre visszamenően érhetőek el. Ez a script segít letölteni a koteslistákat. 
Ha hetente el tudjuk indítani kétszer, vagy be tudjuk rakni utemezőbe akkor magától folyamatosan le fogja tölteni
az aktuális fájlokat. A fájlokat Gzip-el tömörítve tárolja, hogy ne foglaljanak annyi helyet (kb. 74% helymegtakarítás). 

## beállítás fájlok
* letoltott - ez tartalmazza a már letöltött koteslista fájlok dátumait
* modfile - ez a fájl tartalmazza a munkanap áthelyezések dátumait
