"""
main.py: třetí projekt do Engeto Online Python Akademie

autor: Gabriela Hořínková
email: gabriela.lostakova@seznam.cz
"""

import csv
import sys

import requests
from bs4 import BeautifulSoup


def najdi_kod_nazev_url_obce(url):
    """
    Načte HTML stránku z dané URL a vyhledá všechny obce v daném územním celku.

    Pro každou obec získá:
    - číselný kód obce,
    - název obce,
    - URL adresa s detailními výsledky hlasování.

    Args:
        url (str): URL adresa scrapovaného okresu.

    Returns:
        obce (list): Seznam obcí jako trojice hodnot - kód, název a URL s výsledky obce

        Příklad:
            (
            "525588",
            "Bludov",
            "https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ"
            "&xkraj=12&xobec=525588&xvyber=7105"
            )
    """

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    obce = []

    for row in soup.find_all("tr"):  # procházím všechny řádky tabulky (table row)
        kod_ze_stranky = row.find("td", class_="cislo")  # hledám buňku s číselným kódem obce
        nazev_ze_stranky = row.find("td", class_="overflow_name")  # hledám buňku s názvem obce

        if kod_ze_stranky and nazev_ze_stranky:
            kod_obce = kod_ze_stranky.text.strip()
            nazev_obce = nazev_ze_stranky.text.strip()
            a_tag = kod_ze_stranky.find("a")  # hledám odkaz <a> uvnitř buňky s kódem obce
            if a_tag and "href" in a_tag.attrs:  # kontroluji, zda <a> obshuje href
                obec_url = "https://www.volby.cz/pls/ps2017nss/" + a_tag["href"]
                # sestavím úplnou URL adresu dané obce
                obce.append((kod_obce, nazev_obce, obec_url))
    return obce


def zpracuj_obec(kod_obce, nazev_obce, obec_url):
    """Zpracuje volební výsledky pro jednu obec.

    Načte HTML stránku s výsledky hlasování a získá:
    - počet voličů v seznamu,
    - počet vydaných obálek,
    - počet platných hlasů,
    - hlasy pro jednotlivé strany.

    Args:
        kod_obce (str): Číselný kód obce.
        nazev_obce (str): Název obce.
        obec_url (str): URL adresa stránky s výsledky hlasování pro danou obec.

    Returns:
        tuple: Hlavička (list názvů sloupců) a řádek s daty pro obec (list hodnot).

        Příklad:
            (
                ["kód_obce", "název_obce", "voliči_v_seznamu"],
                ["525588", "Bludov", "2504"]
            )
    """

    response = requests.get(obec_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # hledám buňku <td> s atributem headers="sa2" - počet voliců
    volici_obec = soup.find("td", headers="sa2")
    obalky_obec = soup.find("td", headers="sa3")
    platne_hlasy = soup.find("td", headers="sa6")

    if volici_obec and obalky_obec and platne_hlasy:
        # získám text z řádku, odstraňuji (nedělitelnou) mezeru
        volici, obalky, platne = [
            hodnota.text.strip().replace("\xa0", "")
            for hodnota in (volici_obec, obalky_obec, platne_hlasy)
        ]

    else:
        print("Některý údaj nebyl nalezen - nastavuji 0.")
        volici, obalky, platne = "0", "0", "0"

    vysledky = {}
    
    for row in soup.select("table.table tr"):  # hledám po řádcích na stránce tabulku
        radek_data = row.find_all("td")  # hledám buňky <td>
        if len(radek_data) == 5:
            nazev_strany = radek_data[1].text.strip()
            hlasy = radek_data[2].text.strip().replace("\xa0", "")
            vysledky[nazev_strany] = hlasy
    
    hlavicka_csv = (
        ["kód_obce", "název_obce", "voliči_v_seznamu", "vydané_obálky", "platné_hlasy"] 
        + list(vysledky.keys())
    )
    radek = [kod_obce, nazev_obce, volici, obalky, platne] + list(vysledky.values())
   
    return hlavicka_csv, radek


def zpracuj_vsechny_obce(obce):
    """
    Projde všechny obce ze zadaného seznamu obcí a zpracuje jejich volební výsledky.

    Pro každou obec:
    - stáhne detailní stránku s výsledky,
    - získá počet voličů, obálek, platných hlasů a hlasy pro jednotlivé strany,
    - uloží data do jednoho řádku.

    Args:
        obce (list): Seznam obcí jako trojice hodnot - kód obce, název obce, URL s výsledky.

    Returns:
        tuple: Hlavička CSV souboru (názvy sloupců) a seznam řádků s daty pro jednotlivé obce.

        Příklad:
        (
            ["kód_obce", "název_obce", "voliči_v_seznamu"],
            [
                ["525588", "Bludov", "2504"],
                ["525804", "Bohdíkov", "1103"]
            ]
        )
    """
   
    vsechny_radky = [] 
    hlavicka_csv = None

    for kod_obce, nazev_obce, obec_url in obce:
        hlavicka, radek_obce = zpracuj_obec(kod_obce, nazev_obce, obec_url)
        if hlavicka_csv is None:
            hlavicka_csv = hlavicka
        vsechny_radky.append(radek_obce)
    return hlavicka_csv, vsechny_radky


def uloz_vysledky_csv(nazev_souboru, hlavicka_csv, vsechny_radky):
    """    
    Uloží volební výsledky do CSV souboru.

    Vytvoří nový soubor s daným názvem a zapíše do něj:
    - první řádek jako hlavičku (názvy sloupců),
    - další řádky s daty pro jednotlivé obce.

    Args:
        nazev_souboru (str): Název výstupního CSV souboru (např. 'vysledky.csv').
        hlavicka_csv (list): Seznam názvů sloupců pro první řádek.
        vsechny_radky (list): Seznam řádků s daty - každý řádek odpovídá jedné obci.

    Returns:
        None
    """

    with open(nazev_souboru, "w", newline="", encoding="utf-8-sig") as soubor_s_vysledky:
        writer = csv.writer(soubor_s_vysledky, delimiter=";")
        writer.writerow(hlavicka_csv)
        writer.writerows(vsechny_radky)
    

def main():
    """
    Spouští hlavní běh programu pro stažení volebních výsledků z roku 2017 pro vybraný okres.

    Funkce kontroluje správnost vstupních argumentů z příkazové řádky:
    - Musí být zadány dva argumenty:
        - První argument musí být platná URL adresa konkrétního územního celku.
        - Druhý argument musí být název výstupního souboru s příponou .csv.

    Pokud jsou argumenty v pořádku, funkce:
    - Načte seznam obcí z dané URL.
    - Pro každou obec stáhne volební výsledky.
    - Výsledky uloží do zadaného CSV souboru.

    V případě chybných nebo chybějících argumentů program vypíše upozornění a ukončí se.
    """

    if len(sys.argv) != 3:
        print("Nezadán správný počet argumentů")
        return

    url_obce = sys.argv[1]
    vystupni_soubor = sys.argv[2]

    if not url_obce.startswith(
        "https://www.volby.cz/pls/ps2017nss/ps32"
    ):
        print("První argument není platná URL")
        return
    if not vystupni_soubor.endswith(".csv"):
        print("Druhý argument musí být název souboru s příponou .csv")
        return

    obce = najdi_kod_nazev_url_obce(url_obce)
    if not obce:
        print("Nebyly nalezny žádné obce - zkontroluj URL.")
        return
    print(f"STAHUJI DATA Z VYBRANÉHO URL: {url_obce}")
    
    hlavicka_csv, vsechny_radky = zpracuj_vsechny_obce(obce)
    uloz_vysledky_csv(vystupni_soubor, hlavicka_csv, vsechny_radky)
    
    print(f"UKLADAM DO SOUBORU: {vystupni_soubor}")
    print("UKONCUJI election-scraper")

if __name__ == "__main__":
    main()
