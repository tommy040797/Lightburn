# -*- coding: utf-8 -*-
import json
import glob
import Util.Config
import os
import traceback


def getTextGUI(orderid, pfad, delimiter):
    values = pfad.split(delimiter)
    for item in values:
        try:
            file = glob.glob("Zips/" + orderid + "/*.json")
            with open(file[0], "r", encoding="UTF-8") as f:
                data = json.load(f)
                erg = eval(item)
                return erg
        except:
            pass


def getPreviewImage(orderid):
    gui = Util.Config.getGuiConfig()

    file = glob.glob("Zips/" + orderid + "/*.json")
    with open(file[0], "r", encoding="UTF-8") as f:
        data = json.load(f)
        childerin = eval(gui["Vorschau"])
    return childerin


def getOnlyPattern(orderid, delimiter, guistyle):
    specificguipath = Util.Config.getPreviewGUIConfig(guistyle)
    gui = Util.Config.getGuiConfig()
    pfad = Util.Config.getConfig()
    pfad = pfad["PfadZuAllenMotiven"]
    try:
        liste = specificguipath["Bild1"].split(delimiter)
    except:
        return None, 0
    erg = []
    file = glob.glob("Zips/" + orderid + "/*.json")
    with open(file[0], "r", encoding="UTF-8") as f:
        data = json.load(f)
        hits = 0
        for item in liste:
            if "%" in item:
                item = item.replace("%", "")
                try:
                    ergint = pfad + eval(item) + ".png"
                    hits += 1
                    erg.append(ergint)
                except:
                    pass
            elif "$" in item:
                item = item.replace("$", "")
                try:

                    ergint = str(os.getcwd()) + "\Zips\\" + orderid + "\\" + eval(item)
                    hits += 1
                    erg.append(ergint)
                except:
                    pass
    return erg, hits


def getFont(orderid, delimiter):
    gui = Util.Config.getGuiConfig()
    try:
        erg = getTextGUI(orderid, gui["FontBild"], delimiter)
    except:
        erg = getTextGUI(orderid, gui["FontText"], delimiter)
    if erg == None:
        print("Font konnte net gefunden werden")
    return erg


def getEngravingColor(orderid, delimiter):
    gui = Util.Config.getGuiConfig()
    erg = getTextGUI(orderid, gui["EngravingColor"], delimiter)
    return erg


def getComments(orderid, delimiter):
    gui = Util.Config.getGuiConfig()
    erg = getTextGUI(orderid, gui["Kommentare"], delimiter)
    if erg == None:
        print("Kommentar konnte net gefunden werden")
    return erg


def getIfOnlyText(orderid):
    gui = Util.Config.getGuiConfig()

    file = glob.glob("Zips/" + orderid + "/*.json")
    with open(file[0], "r", encoding="UTF-8") as f:
        data = json.load(f)
        try:
            childerin1 = eval(gui["TextOnly1"])
            childerin2 = eval(gui["TextOnly2"])
            childerin3 = eval(gui["TextOnly3"])
        except:
            return False
        if childerin1 == "" and childerin2 == "" and childerin3 == "":
            return False
        else:
            return True


def checkIfImage(orderid):
    gui = Util.Config.getGuiConfig()
    file = glob.glob("Zips/" + orderid + "/*.json")
    with open(file[0], "r", encoding="UTF-8") as f:
        data = json.load(f)
        try:
            childerin1 = eval(gui["TextOnly1"])
            childerin2 = eval(gui["TextOnly2"])
            childerin3 = eval(gui["TextOnly3"])
        except:
            return False
        if childerin1 == "" and childerin2 == "" and childerin3 == "":
            return False
        else:
            return True


def getAsin(orderid, delimiter):
    gui = Util.Config.getGuiConfig()
    erg = getTextGUI(orderid, gui["Identifier"], delimiter)
    return erg


def getImage(orderid, pfad, delimiter):
    gui = Util.Config.getGuiConfig()
    pfadteil = Util.Config.getConfig()
    pfadteil = pfadteil["PfadZuAllenMotiven"]
    file = glob.glob("Zips/" + orderid + "/*.json")
    try:
        liste = pfad.split(delimiter)
    except:
        return None, 0
    with open(file[0], "r", encoding="UTF-8") as f:
        data = json.load(f)
        for item in liste:
            if "%" in item:
                pfad = item.replace("%", "")
                try:
                    if (eval(pfad)) == "":
                        return None
                    ergint = pfadteil + eval(pfad) + ".png"
                    return ergint
                except:
                    return None
            elif "$" in item:
                pfad = item.replace("$", "")
                try:
                    if (eval(pfad)) == "":
                        return None
                    ergint = str(os.getcwd()) + "\Zips\\" + orderid + "\\" + eval(pfad)
                    return ergint
                except:
                    return None


def getText(orderid, pfad):
    try:
        file = glob.glob("Zips/" + orderid + "/*.json")
        with open(file[0], "r", encoding="UTF-8") as f:
            data = json.load(f)
            erg = eval(pfad)
            return erg
    except Exception as e:
        # traceback.print_exception(e)
        raise
