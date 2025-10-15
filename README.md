# Engeto-pa-3-projekt

**Třetí projekt do Engeto Online Python Akademie**


# Popis projektu
Election Scraper – Ukázkový projekt

Tento projekt slouží k automatickému stažení výsledků voleb z webu volby.cz  a jejich uložení do souboru ve formátu CSV.


# Instalace knihoven
Knihovny použité v projektu jsou uvedeny v souboru 'requirements.txt'.
Instalaci lze provést pomocí následujícího příkazu:

```
pip3 install -r requirements.txt
```


# Spuštění

Spuštění souboru main.py v rámci příkazového řádku obsahuje dva povinné argumenty.

```
python main.py <odkaz_uzemniho_celku> <vysledky_voleb>
```

Výsledky se uloží do souboru s příponou .csv.


# Ukázka projektu

## Výsledky hlasování pro okres Šumperk

1. argument – https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7105

2. argument – vysledky_sumperk.csv

## Spuštění programu 

python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7105" vysledky_sumperk.csv

## Průběh stahování

STAHUJI DATA Z VYBRANÉHO URL: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7105
UKLADAM DO SOUBORU: vysledky_sumperk.csv
UKONCUJI election-scraper

## Částečný výstup

Výsledný CSV soubor obsahuje data ve struktuře:

kód_obce;název_obce;voliči_v_seznamu;vydané_obálky;platné_hlasy;...
525588;Bludov;2504;1632;1615;178;0;0;123;1;133;112;19;17;10;1;0;110;3;38;513;1;0;136;0;3;3;2;208;4;-
525804;Bohdíkov;1103;640;634;33;2;2;42;0;40;64;6;7;5;2;0;44;0;11;227;0;1;36;0;0;0;0;110;2;-
...
