import csv
import Util.Config as Config
import requests

import os
from zipfile import ZipFile
import glob
import xml.etree.ElementTree as ET


# filter die ctabspace txtDateinach Paramtetern in filter.ini
def parseCsv(csvname, idspalte):
    liste = Config.getFilterConfig()
    dictlist = []
    with open(csvname, newline="", encoding="utf8") as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter="\t")
        for c in spamreader:
            counter = 1
            erg = multivalueCompare(liste, c)
            if erg == True:
                if any(x[idspalte] == c[idspalte] for x in dictlist):
                    counter += 1
                    c[idspalte] = c[idspalte] + " " + str(counter) + "."
                dictlist.append(c)
            else:
                counter = 1
    return dictlist


def downloadZip(url):
    response = requests.get(url)
    if not response.status_code == 200:
        print("DOWNLOAD FEHLGESCHLAGEN")
        return None
    return response.content


def downloadAndUnpack(spaltennamefürdownload, bestellungsidspaltenname):
    if os.path.isdir("Zips/" + bestellungsidspaltenname):
        return
    answer = downloadZip(spaltennamefürdownload)
    if answer == None:
        exit()
    with open("Zips/" + bestellungsidspaltenname + ".zip", mode="wb") as file:
        file.write(answer)
    with ZipFile("Zips/" + bestellungsidspaltenname + ".zip", "r") as f:
        f.extractall("Zips/" + bestellungsidspaltenname)
    os.remove("Zips/" + bestellungsidspaltenname + ".zip")


def multivalueCompare(dict, currentc):
    keys = list(dict.keys())
    values = list(dict.values())
    erg = True
    for item in keys:
        if values[keys.index(item)] in currentc[item]:
            pass
        else:
            erg = False
            return erg
    return erg


def getTemplates():
    erg = []
    file = glob.glob("Templates/*.lbrn")
    for item in file:
        dummy = item.split("\\")
        erg.append(dummy[1])
    return erg


def getXML(name):
    tree = ET.parse("Templates/" + name)
    return tree
