# -*- coding: utf-8 -*-
import json
import glob
import Util.Config
import os
import traceback


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
    liste = specificguipath["Bild1"].split(delimiter)
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


def getFont(orderid):
    gui = Util.Config.getGuiConfig()
    file = glob.glob("Zips/" + orderid + "/*.json")
    with open(file[0], "r", encoding="UTF-8") as f:
        data = json.load(f)
        try:
            fontBild = eval(gui["FontBild"])
        except:
            print("font kann nicht gelesen werden, bitte config prüfen")
        try:
            fontText = eval(gui["FontText"])
        except:
            return fontBild
        if getIfOnlyText(orderid):
            return fontText
        else:
            return fontBild


def getEngravingColor(orderid):
    gui = Util.Config.getGuiConfig()
    file = glob.glob("Zips/" + orderid + "/*.json")
    with open(file[0], "r", encoding="UTF-8") as f:
        data = json.load(f)
        engravingColor = eval(gui["EngravingColor"])
    return engravingColor


def getTextBelow(orderid):
    gui = Util.Config.getGuiConfig()
    file = glob.glob("Zips/" + orderid + "/*.json")
    with open(file[0], "r", encoding="UTF-8") as f:
        try:
            data = json.load(f)
            childerin = eval(gui["TextUnterBild"])
            return childerin
        except KeyError:
            return ""


# macht garnichts aktuell
def getTextBelowScale(orderid):
    file = glob.glob("Zips/" + orderid + "/*.json")
    with open(file[0], "r", encoding="UTF-8") as f:
        data = json.load(f)
        try:
            scale = data["customizationData"]["children"][0]["children"][0]["children"][
                4
            ]["children"][2]["children"][0]["buyerPlacement"]["scale"]["scaleX"]
        except:
            return None
    return scale


# macht auch nichts, wird durch Matrixtrafo direkt aus Json umgerechnet
def getTextBelowRotation(orderid):
    file = glob.glob("Zips/" + orderid + "/*.json")
    with open(file[0], "r", encoding="UTF-8") as f:
        data = json.load(f)
        try:
            scale = data["customizationData"]["children"][0]["children"][0]["children"][
                4
            ]["children"][2]["children"][0]["buyerPlacement"]["angleOfRotation"]
        except:
            return None
    return scale


def getTextAbove(orderid):
    gui = Util.Config.getGuiConfig()
    file = glob.glob("Zips/" + orderid + "/*.json")
    with open(file[0], "r", encoding="UTF-8") as f:
        try:
            data = json.load(f)
            childerin = eval(gui["TextUeberBild"])
            return childerin
        except KeyError:
            return ""


# macht garnichts aktuell
def getTextAboveScale(orderid):
    file = glob.glob("Zips/" + orderid + "/*.json")
    with open(file[0], "r", encoding="UTF-8") as f:
        data = json.load(f)
        try:
            scale = data["customizationData"]["children"][0]["children"][0]["children"][
                4
            ]["children"][2]["children"][1]["buyerPlacement"]["scale"]["scaleX"]
        except:
            return None
    return scale


# macht auch nichts, wird durch Matrixtrafo direkt aus Json umgerechnet
def getTextAboveRotation(orderid):
    file = glob.glob("Zips/" + orderid + "/*.json")
    with open(file[0], "r", encoding="UTF-8") as f:
        data = json.load(f)
        try:
            scale = data["customizationData"]["children"][0]["children"][0]["children"][
                4
            ]["children"][2]["children"][1]["buyerPlacement"]["angleOfRotation"]
        except:
            return None
    return scale


def getComments(orderid):
    gui = Util.Config.getGuiConfig()
    file = glob.glob("Zips/" + orderid + "/*.json")
    with open(file[0], "r", encoding="UTF-8") as f:
        data = json.load(f)
        erg = eval(gui["Kommentare"])
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


def getFirstLine(orderid):
    gui = Util.Config.getGuiConfig()

    file = glob.glob("Zips/" + orderid + "/*.json")
    with open(file[0], "r", encoding="UTF-8") as f:
        data = json.load(f)
        try:
            childerin1 = eval(gui["TextOnly1"])
        except:
            return ""
    return childerin1


def getSecondLine(orderid):
    gui = Util.Config.getGuiConfig()

    file = glob.glob("Zips/" + orderid + "/*.json")
    with open(file[0], "r", encoding="UTF-8") as f:
        data = json.load(f)
        try:
            childerin1 = eval(gui["TextOnly2"])
        except:
            return ""
    return childerin1


def getThirdLine(orderid):
    gui = Util.Config.getGuiConfig()

    file = glob.glob("Zips/" + orderid + "/*.json")
    with open(file[0], "r", encoding="UTF-8") as f:
        data = json.load(f)
        try:
            childerin1 = eval(gui["TextOnly3"])
        except:
            return ""
    return childerin1


def getAsin(orderid):
    gui = Util.Config.getGuiConfig()

    file = glob.glob("Zips/" + orderid + "/*.json")
    with open(file[0], "r", encoding="UTF-8") as f:
        data = json.load(f)
        try:
            childerin1 = eval(gui["Identifier"])
        except:
            return ""
    return childerin1


def getImage(orderid, pfad):
    gui = Util.Config.getGuiConfig()
    pfadteil = Util.Config.getConfig()
    pfadteil = pfadteil["PfadZuAllenMotiven"]
    file = glob.glob("Zips/" + orderid + "/*.json")
    with open(file[0], "r", encoding="UTF-8") as f:
        data = json.load(f)
        if "%" in pfad:
            pfad = pfad.replace("%", "")
            try:
                if (eval(pfad)) == "":
                    return None
                ergint = pfadteil + eval(pfad) + ".png"
                return ergint
            except:
                return None
        elif "$" in pfad:
            pfad = pfad.replace("$", "")
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
        print(
            "kein problem, den pfad gibts nur nichtbei der bestelltung"
            + orderid
            + ", bei der methode showtext"
            + pfad
        )
        return None
