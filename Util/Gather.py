import csv
import Util.Config as Config
import requests
import os
from zipfile import ZipFile
import glob
import xml.etree.ElementTree as ET


# filter die ctabspace txtDateinach Paramtetern in filter.ini
def parseCsv(csvname):
    liste = Config.getFilterConfig()
    dictlist = []
    with open(csvname, newline="", encoding="utf8") as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter="\t")
        for c in spamreader:
            erg = multivalueCompare(liste, c)
            if erg == True:
                dictlist.append(c)
    return dictlist


def downloadZip(url):
    response = requests.get(url)
    print(response)
    return response.content


def downloadAndUnpack(spaltennamefürdownload, bestellungsid):
    answer = downloadZip(spaltennamefürdownload)
    with open("Zips/" + bestellungsid + ".zip", mode="wb") as file:
        file.write(answer)
    with ZipFile("Zips/" + bestellungsid + ".zip", "r") as f:
        f.extractall("Zips/" + bestellungsid)
    os.remove("Zips/" + bestellungsid + ".zip")


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
