import Util.Config
import Util.Jsonprocessing as Json
from PIL import Image
import Util.Imageprocessing
import Util.Gather
import xml.etree.ElementTree as ET
import glob
import json
import os
import math


def processxml(template, delimiter, orderid, targetbreitelb, maxhoehelb, patternImg):
    imageDict, _ = Util.Config.getXMLConfig(template.split(".")[0])
    rest = Util.Config.getConfig()
    keys = []
    keylist = list(imageDict.keys())
    valuelist = list(imageDict.values())
    xml = Util.Gather.getXML(template)
    root = xml.getroot()
    for key in keylist:
        keys.append(key.split(delimiter))

    file = glob.glob("Zips/" + orderid + "/*.json")
    # iteriere config liste durch
    for key in keys:
        try:
            with open(file[0], "r", encoding="UTF-8") as f:
                data = json.load(f)
                erg = ""
                key[1] = key[1].capitalize()
                values = valuelist[keys.index(key)].split(delimiter)
                # Wenn rohe zuordnung, und der letzte eintrag der liste gewünscht ist valueElement ist das value element!!!
                if key[2] == "zuordnung":
                    erg, fail = Pfadparsing(
                        values, rest["PfadZuAllenMotiven"], orderid, erg, data
                    )

                    eval(key[0]).set(key[1], str(erg))
                elif key[2] == "bildbreite":
                    img = eval(values[0]).get(values[1])
                    try:
                        img = Image.open(img)
                    except:
                        print("template erwartet ein bild")
                        return
                    erg = str(
                        Util.Imageprocessing.getscale(targetbreitelb, maxhoehelb, img)[
                            0
                        ]
                    )
                    eval(key[0]).set(key[1], erg)
                elif key[2] == "bildhoehe":
                    img = eval(values[0]).get(values[1])
                    img = Image.open(img)
                    erg = str(
                        Util.Imageprocessing.getscale(targetbreitelb, maxhoehelb, img)[
                            1
                        ]
                    )
                    eval(key[0]).set(key[1], erg)
                elif key[2] == "matrixtrafo":
                    try:
                        angle = eval(values[0])
                    except:
                        angle = 0
                    # mit dem uhrzeigersinn rotieren
                    angle = -angle
                    # string in verwertbare floatwerte in einer liste splitten
                    try:
                        matrixstringliste = eval(key[0]).text.split(" ")
                    except:
                        matrixstringliste = ["0", "0", "0", "0", "0", "0"]
                    matrixfloatliste = [float(i) for i in matrixstringliste]
                    targetliste = [0, 0, 0, 0, 0, 0]
                    # matrixmultiplikation mit der translationsmatrix
                    targetliste[0] = matrixfloatliste[0] * math.cos(
                        math.radians(angle)
                    ) + matrixfloatliste[2] * math.sin(math.radians(angle))
                    targetliste[1] = matrixfloatliste[1] * math.cos(
                        math.radians(angle)
                    ) + matrixfloatliste[3] * math.sin(math.radians(angle))
                    targetliste[2] = matrixfloatliste[0] * -math.sin(
                        math.radians(angle)
                    ) + matrixfloatliste[2] * math.cos(math.radians(angle))
                    targetliste[3] = matrixfloatliste[1] * -math.sin(
                        math.radians(angle)
                    ) + matrixfloatliste[3] * math.cos(math.radians(angle))
                    targetliste[4] = matrixfloatliste[4]
                    targetliste[5] = matrixfloatliste[5]
                    matrixstringliste = [str(i) for i in targetliste]
                    s1 = ""
                    for x in matrixstringliste:
                        s1 += " " + x
                    # führendes leerzeichen entfernen sonst bug
                    string = s1[1:]
                    eval(key[0]).text = string
                elif key[2] == "laser":
                    farbe = eval(values[0])
                    pfad = eval(key[0])

                    silber, schwarz = Util.Config.getLaserColors()
                    if farbe == "Silber":
                        erg = silber[pfad.tag]
                    eval(key[0]).set(key[1], str(erg))
                # xml.write("test.xml")
            if not patternImg == None:
                eval(keys[0][0]).set(
                    keys[0][1], str(os.getcwd()) + "\\Util\\pattern.png"
                )
            xml.write("Util/output.lbrn")
        except:
            print(key + "hat einen error ausgeworfen")

    # print(keys)


def Pfadparsing(values, pfad, orderid, erg, data):
    fail = 0
    for valueElement in values:
        valueElement = str(valueElement)
        if "%" in valueElement:
            valueElement = valueElement.replace("%", "")
            try:
                erg = pfad + eval(valueElement) + ".png"
            except:
                fail += 1
                pass
        elif "$" in valueElement:
            valueElement = valueElement.replace("$", "")
            try:
                erg = str(os.getcwd()) + "\Zips\\" + orderid + "\\" + eval(valueElement)
            except:
                fail += 1
                pass
        else:
            erg = eval(valueElement)
    return erg, fail
