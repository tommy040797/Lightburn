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
import logging
import traceback
import numpy as np

import Util.Jsonprocessing

logger = logging.getLogger(__name__)


def processxml(
    template,
    delimiter,
    orderid,
    targetbreitelb,
    maxhoehelb,
    patternImg,
    skalierungsfaktor,
    pixelInMM,
):
    try:
        imageDict, _ = Util.Config.getXMLConfig(template.split(".")[0])
    except:
        print("Problem beim Templateconfig lesen")
    rest = Util.Config.getConfig()
    keys = []
    keylist = list(imageDict.keys())
    valuelist = list(imageDict.values())
    try:
        xml = Util.Gather.getXML(template)
    except:
        print("lightburn template file konnte nicht geladen werden")
        return
    root = xml.getroot()
    try:
        for key in keylist:
            keys.append(key.split(delimiter))
    except:
        print("Problem beim Parsen der Keys der Templateconfig")

    file = glob.glob("Zips/" + orderid + "/*.json")
    if file == None:
        print("JSON konnte nicht gelesen werden")
        return
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
                    for item in values:
                        try:
                            angle = eval(item)
                            continue
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
                    for item in values:
                        try:
                            farbe = eval(item)
                            continue
                        except:
                            pass
                    pfad = eval(key[0])

                    silber, schwarz = Util.Config.getLaserColors()
                    if farbe == "Silber":
                        erg = silber[pfad.tag]
                    elif farbe == "Schwarz":
                        erg = schwarz[pfad.tag]
                    eval(key[0]).set(key[1], str(erg))
                elif key[2] == "matrixskalierung":
                    try:
                        logger.info("Font für scaling")
                        fontdict = Util.Config.getFontSizeConfig()
                        font = eval(values[1])
                        fontsize = float(fontdict[font])
                    except Exception as e:
                        # traceback.print_exception(e)
                        # logger.exception(e)
                        logger.info("keine Fontspezialisierung, oder bild")
                        fontsize = 1
                    try:
                        scaleX = eval(values[0])["scaleX"]
                        scaleY = eval(values[0])["scaleY"]

                    except Exception as e:
                        # traceback.print_exception(e)
                        logger.info(
                            "kein Custom Bild, deswegen keine positionsverschiebung"
                        )
                        continue
                    faktorX = scaleX * (1 / fontsize) * skalierungsfaktor
                    faktorY = scaleY * (1 / fontsize) * skalierungsfaktor
                    try:
                        matrixstringliste = eval(key[0]).text.split(" ")
                    except:
                        matrixstringliste = ["0", "0", "0", "0", "0", "0"]
                    matrixfloatliste = [float(i) for i in matrixstringliste]
                    targetliste = [0, 0, 0, 0, 0, 0]
                    # matrixmultiplikation mit der translationsmatrix
                    targetliste[0] = matrixfloatliste[0] * faktorX
                    targetliste[1] = matrixfloatliste[1] * faktorX
                    targetliste[2] = matrixfloatliste[2] * faktorY
                    targetliste[3] = matrixfloatliste[3] * faktorY
                    targetliste[4] = matrixfloatliste[4]
                    targetliste[5] = matrixfloatliste[5]
                    matrixstringliste = [str(i) for i in targetliste]
                    s1 = ""
                    for z in matrixstringliste:
                        s1 += " " + z
                    # führendes leerzeichen entfernen sonst bug
                    string = s1[1:]
                    eval(key[0]).text = string
                elif key[2] == "matrixtranslation":
                    try:
                        mitteVonItemInPixeln = (
                            (
                                (eval(values[3])["width"] * eval(values[4])["scaleX"])
                                * 0.5
                            )
                            + eval(values[2])["x"]
                            - eval(values[0])["x"],
                            (
                                eval(values[3])["height"]
                                * eval(values[4])["scaleY"]
                                * 0.5
                            )
                            + eval(values[2])["y"],
                        )
                        mitteVonPlacementPane = (
                            0.5 * eval(values[1])["width"],
                            eval(values[1])["height"] * 0.5 + eval(values[0])["y"],
                        )
                        verschiebevalue = np.subtract(
                            mitteVonItemInPixeln, mitteVonPlacementPane
                        )
                        verschiebevalue[1] = verschiebevalue[1] * -1
                        xverschiebung = verschiebevalue[0] / pixelInMM
                        yverschiebung = verschiebevalue[1] / pixelInMM
                        try:
                            matrixstringliste = eval(key[0]).text.split(" ")
                        except:
                            matrixstringliste = ["0", "0", "0", "0", "0", "0"]
                        matrixfloatliste = [float(i) for i in matrixstringliste]
                        targetliste = [0, 0, 0, 0, 0, 0]
                        # matrixmultiplikation mit der translationsmatrix
                        targetliste[0] = matrixfloatliste[0]
                        targetliste[1] = matrixfloatliste[1]
                        targetliste[2] = matrixfloatliste[2]
                        targetliste[3] = matrixfloatliste[3]
                        targetliste[4] = (
                            matrixfloatliste[0] * xverschiebung
                            + matrixfloatliste[2] * yverschiebung
                            + matrixfloatliste[4]
                        )
                        targetliste[5] = (
                            matrixfloatliste[1] * xverschiebung
                            + matrixfloatliste[3] * yverschiebung
                            + matrixfloatliste[5]
                        )
                        matrixstringliste = [str(i) for i in targetliste]
                        s1 = ""
                        for x in matrixstringliste:
                            s1 += " " + x
                        # führendes leerzeichen entfernen sonst bug
                        string = s1[1:]
                        eval(key[0]).text = string
                    except:
                        pass
            if not patternImg == None:
                eval(keys[0][0]).set(
                    keys[0][1], str(os.getcwd()) + "\\Util\\pattern.png"
                )
            try:
                xml.write("Util/output.lbrn")
            except:
                print(
                    "lightburn File konnte nicht geschrieben werden, evtl. Schreibgeschützt, evtl. PC neu starten"
                )
                return
        except Exception as e:
            traceback.print_exception(e)
            print(
                key[0]
                + "hat einen error ausgeworfen, bitte anderes Template verwenden oder Christian kontaktieren"
            )


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
            try:
                erg = Util.Jsonprocessing.getText(orderid, valueElement)
                return erg, fail
            except:
                fail += 1
                erg = ""
                print(
                    "Anscheinend Champagnerfarben, da erster Pfad nicht gefunden werden konnte"
                )
                pass
    return erg, fail
