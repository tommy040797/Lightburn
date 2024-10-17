# -*- coding: utf-8 -*-
import Util.Config
import Util.Gather
import Util.Imageprocessing
import Util.Order as Orders

# import Util.UIEnhance
import tkinter as tk
from tkinter import font as f
from PIL import ImageTk, Image
import subprocess
import Util.Jsonprocessing
import os
import cProfile as profile
import pstats
import traceback
import logging
import shutil


# TODO: logs beim gui lesen, layoutmanager skalierung, vorschau mit template, farbe wenn in text was drin steht, unterodner von bildern miteinbeziehen
try:
    os.remove("logs.log")
except:
    pass
logger = logging.getLogger(__name__)

# Config lesen
try:
    configdict = Util.Config.getConfig()
    inputfile = configdict["Inputfile"]
    zipdownloadspalte = configdict["NameDerSpalteFuerZipDownload"]
    anzeigenzielbreite = int(configdict["GuiBildbreite"])
    anzeigenmaxhöhe = int(configdict["GuiBildhoehe"])
    nodownload = configdict["DebugNoDownload"]
    skalierungsfaktor = float(configdict["GroessenskalierungswertLightburn"])
    pixelinmm = float(configdict["PixelInMM"])
    targetbreitelb = int(configdict["Flaschenbreite"])
    maxhoehelb = int(configdict["Flaschenhoehe"])

    standardTemplate = configdict["Standardtemplate"]
    delimiter = configdict["delimiterFuerConfig"]
    pfadzulightburn = configdict["PfadZuLightburn"]
    pfadzuirfan = configdict["PfadZuIrfanview"]
    orderIdSpaltenName = configdict["ID-Spaltenname"]
    pfadzuallenmotiven = configdict["PfadZuAllenMotiven"]
except Exception as e:
    traceback.print_exc(e)
    print(
        "Standardconfig wurde nicht gefunden, oder ein Fehler liegt vor, Programm wird beendet"
    )
    quit()

bildistda = True
profiling = False
global vorschauobjekte
vorschauobjekte = {}
global patternselectors
patternselectors = []


def updatePreviewUI(dummy):
    global currentPatternImage
    guiTemplateToUse = Util.Config.getXMLConfig(template.get().split(".")[0])[1]["gui"]
    builddict = Util.Config.getPreviewGUIConfig(guiTemplateToUse)
    textHandlingGUI(ordernumber.get(), guiTemplateToUse, builddict)
    imageHandlingGUI(ordernumber.get())


def previewUI(dummy):
    global bildistda
    guiTemplateToUse = Util.Config.getXMLConfig(template.get().split(".")[0])[1]["gui"]
    builddict = Util.Config.getPreviewGUIConfig(guiTemplateToUse)
    if guiTemplateToUse == "Bild":
        bildistda = True
    else:
        bildistda = False
    # Frame Bauen
    for item in vorschauobjekte:
        try:
            vorschauobjekte[item].destroy()
        except Exception as e:
            traceback.print_exception(e)
            print("deleten ging nicht")
    for idx, item in enumerate(patternselectors):
        try:
            patternselectors[idx][2].destroy()
        except:
            pass
    try:
        vorschauobjekte.clear()
        patternselectors.clear()
    except Exception as e:
        traceback.print_exception(e)

    keylist = list(builddict.keys())
    valuelist = list(builddict.values())
    counter = 0
    for idx, item in enumerate(keylist):
        nummer = idx
        if guiTemplateToUse == "Bild" or guiTemplateToUse == "Waagerecht":
            vorschauobjekte[item] = tk.Label(
                previewFrame,
                highlightbackground="blue",
                highlightthickness=2,
                wraplength=0,
            )
            vorschauobjekte[item].pack(side="top", fill="both", expand="yes")
            if "Bild" in item:
                _, hits = Util.Jsonprocessing.getOnlyPattern(
                    ordernumber.get(), delimiter, guiTemplateToUse
                )
            else:
                hits = 0
            if "Bild" in item and hits > 0:
                patternselectors.append([])
                # patternselectors[counter][0] = liste, [1] = stringvar, [2] = optionmenu
                patternselectors[counter].append([])
                patternselectors[counter][0], _ = Util.Jsonprocessing.getOnlyPattern(
                    ordernumber.get(), delimiter, "Bild"
                )
                patternselectors[counter].append(tk.StringVar())
                patternselectors[counter][1].set(patternselectors[counter][0][-1])
                patternselectors[counter].append(
                    tk.OptionMenu(
                        patternFrame,
                        patternselectors[counter][1],
                        *patternselectors[counter][0],
                        command=updatePreviewUI,
                    )
                )
                patternselectors[counter][2].pack(anchor="w")
                counter += 1
        elif guiTemplateToUse == "Senkrecht":
            vorschauobjekte[item] = tk.Label(
                previewFrame,
                highlightbackground="blue",
                highlightthickness=2,
                wraplength=1,
            )
            vorschauobjekte[item].pack(side="left", fill="both", expand="yes")
    setBackground()
    if not pattern.get() == "nochkeinsda":
        updatePreviewUI(None)


def updateAugmentUI(objekte):
    breitegrid = int(Util.Config.getUIColor()["Gridbreite"])
    hoehegrid = int(Util.Config.getUIColor()["Gridhoehe"])
    framehoehe = int(Util.Config.getUIColor()["Framehoehe"])
    framebreite = int(Util.Config.getUIColor()["Framebreite"])
    todo = Util.Config.getAugmentedUI()
    keys = []
    keylist = list(todo.keys())
    valuelist = list(todo.values())
    try:
        for key in keylist:
            keys.append(key.split(delimiter))
        logger.info("Keys gesplittet")
    except Exception as e:
        logger.exception(e)
    for key in keys:
        nummer = int(key[2]) + breitegrid * (int(key[1]) - 1) - 1
        if key[0] == "showimage":
            img = Util.Jsonprocessing.getImage(
                ordernumber.get(), valuelist[keys.index(key)], delimiter
            )
            objekte[nummer][1].configure(image="")
            objekte[nummer][1].image = None
            if not img == None:
                objekte[nummer][2].set(img)
                try:
                    bild = Image.open(img)
                except:
                    print(img + "kann nicht geöffnet werden")
                    return None
                size = Util.Imageprocessing.getscale(
                    min(framehoehe, framebreite) * 0.75,
                    min(framehoehe, framebreite) * 0.75,
                    bild,
                )
                bild = bild.resize(
                    size,
                    Image.Resampling.NEAREST,
                )
                bild = ImageTk.PhotoImage(bild)
                # objekte[nummer][0].configure(text="bild")
                objekte[nummer][1].configure(image=bild)
                objekte[nummer][1].image = bild
            else:
                objekte[nummer][1].configure(
                    image="", text="An diesem Pfad gibt es kein Bild"
                )
                objekte[nummer][1].image = None
                objekte[nummer][1].configure(image="")
        if key[0] == "showtext":
            ## header = 0, textfenster = 1 - laenge von config file
            values = valuelist[keys.index(key)].split(delimiter)
            for i in range(len(values)):
                objekte[nummer][i + 1].configure(text="")

            for i in range(len(values)):
                objekte[nummer][i + 1].config(
                    text=Util.Jsonprocessing.getTextGUI(
                        ordernumber.get(), values[i], delimiter
                    )
                )


def augmentUI(parent):
    def preview(evt):
        try:  # try catch um deselection von anderer liste zu ignorieren
            w = evt.widget
            ziel = 0
            for i in range(breitegrid * hoehegrid):
                if w in objekte[i]:
                    ziel = i
            nummer = int(w.curselection()[0])
            value = w.get(nummer)
            bild = ImageTk.PhotoImage(
                Image.open(pfadzuallenmotiven + value).resize(
                    bildgroese, Image.Resampling.NEAREST
                )
            )
            objekte[ziel][4].configure(image=bild)
            objekte[ziel][4].image = bild
        except:
            pass

    def putasactive(evt):
        try:
            nummer = int(objekte[evt][2].curselection()[0])
            value = objekte[evt][2].get(nummer)
            pattern.set(pfadzuallenmotiven + value)
            updatePreviewUI(None)
        except Exception as e:
            logger.exception(e)
            traceback.print_exc()

    def useThisImg(evt):
        try:
            pattern.set(evt.get())
            updatePreviewUI(None)
        except Exception as e:
            logger.exception(e)
            traceback.print_exc()

    try:
        todo = Util.Config.getAugmentedUI()
        breitegrid = int(Util.Config.getUIColor()["Gridbreite"])
        hoehegrid = int(Util.Config.getUIColor()["Gridhoehe"])
        framehoehe = int(Util.Config.getUIColor()["Framehoehe"])
        framebreite = int(Util.Config.getUIColor()["Framebreite"])
        bildgroese = (int(framehoehe / 4.4), int(framehoehe / 4.4))
        logger.info("AugmentedUI gelesen")
    except Exception as e:
        traceback.print_exception(e)
        logger.exception(e)
        print("Problem beim GUI Custom Config lesen")
    keys = []
    keylist = list(todo.keys())
    valuelist = list(todo.values())
    try:
        for key in keylist:
            keys.append(key.split(delimiter))
        logger.info("Keys gesplittet")
    except Exception as e:
        logger.exception(e)

    # gridsanlegen
    frames = []
    objekte = []
    j = 0
    for i in range(breitegrid * hoehegrid):
        objekte.append([])
        logger.info("frame mit nummer %f wird angelegt", i + 1)
        frames.append(
            tk.Frame(
                parent,
                highlightbackground="yellow",
                highlightthickness=2,
                height=framehoehe,
                width=framebreite,
            )
        )
        frames[i].pack_propagate(0)
        if i % breitegrid == 0:
            j += 1
        frames[i].grid(row=j, column=(i % breitegrid) + 1)
    for key in keys:
        nummer = int(key[2]) + breitegrid * (int(key[1]) - 1) - 1
        if key[0] == "bilderauswahl":

            files = []
            for file in os.listdir(valuelist[keys.index(key)]):
                if file.endswith(".png"):
                    files.append(file)
            # header = 0, frame = 1, listbox = 2, scrollbar = 3, previewbild = 4, button = 5
            objekte[nummer].append(
                tk.Label(frames[nummer], text=key[3], wraplength=framebreite - 20)
            )
            objekte[nummer][0].pack(side="top", anchor="n")
            objekte[nummer].append(
                tk.Frame(
                    frames[nummer],
                    padx=10,
                ),
            )
            objekte[nummer][1].pack(side="top", anchor="nw", fill="x")
            objekte[nummer].append(
                tk.Listbox(
                    objekte[nummer][1],
                    width=int(framebreite / 8),
                    height=int(framehoehe / 27),
                )
            )
            objekte[nummer][2].pack(side="left", anchor="w")
            objekte[nummer].append(
                tk.Scrollbar(
                    objekte[nummer][1],
                    orient="vertical",
                )
            )
            objekte[nummer][3].config(command=objekte[nummer][2].yview)
            objekte[nummer][3].pack(side="left", fill="y", anchor="w")
            objekte[nummer][2].config(yscrollcommand=objekte[nummer][3].set)
            for item in files:
                objekte[nummer][2].insert("end", item)
            objekte[nummer][2].bind("<<ListboxSelect>>", preview)
            objekte[nummer].append(tk.Label(frames[nummer]))
            objekte[nummer][4].pack(side="left", padx=5)
            objekte[nummer].append(
                tk.Button(
                    frames[nummer],
                    text="Bild übernehmen",
                )
            )
            objekte[nummer][5].config(command=lambda t=nummer: putasactive(t))
            objekte[nummer][5].pack(side="right", padx=5)
        if key[0] == "showimage":
            # header = 0, bild = 1, name des bildes = 2, button = 3
            objekte[nummer].append(
                tk.Label(frames[nummer], text=key[3], wraplength=framebreite - 20)
            )
            objekte[nummer][0].pack(side="top", anchor="n")
            objekte[nummer].append(
                tk.Label(
                    frames[nummer],
                    padx=10,
                    pady=10,
                )
            )
            objekte[nummer][1].pack()
            objekte[nummer].append(tk.StringVar())
            objekte[nummer].append(
                tk.Button(
                    frames[nummer],
                    text="Dieses Bild verwenden",
                )
            )
            objekte[nummer][3].config(
                command=lambda t=objekte[nummer][2]: useThisImg(t)
            )
            objekte[nummer][3].pack(side="bottom", pady=5)
        if key[0] == "showtext":
            ## header = 0, textfenster = 1 - laenge von config file
            objekte[nummer].append(
                tk.Label(frames[nummer], text=key[3], wraplength=framebreite - 20)
            )
            objekte[nummer][0].pack(side="top", anchor="n")
            values = valuelist[keys.index(key)].split(delimiter)
            for i in range(len(values)):
                objekte[nummer].append(
                    tk.Label(
                        frames[nummer], padx=10, pady=10, wraplength=framebreite - 20
                    )
                )
                objekte[nummer][i + 1].pack()

    return objekte


def IrfanUI(parent, gridx, gridy, rowspan, columnspan, pack):

    def openIrfan():
        patternpfad = pattern.get()
        if pfadzuallenmotiven not in patternpfad:
            allemotive = False
        else:
            allemotive = True
        oeffnen = False
        for item in vorschauobjekte:
            if "Bild" in item:
                oeffnen = True
                break

        if oeffnen and not allemotive:
            try:
                shutil.copyfile(patternpfad, patternpfad + "original.png")
                subprocess.call(
                    [
                        pfadzuirfan,
                        patternpfad,
                    ]
                )
                logger.info("IrfanView gestartet")
                select(ordernumber.get())
            except Exception as e:
                traceback.print_exception(e)
                logger.exception(e)
                logger.info("IrfanView kann nicht gestartet werden")
        else:
            return

    def reset():
        if not Util.Jsonprocessing.getIfOnlyText(ordernumber.get()):
            try:
                patternpfad = pattern.get()
                try:
                    shutil.copyfile(patternpfad + "original.png", patternpfad)
                except:
                    logger.warning("Bild konnte nicht zurückgesetzt werden")
                logger.info("Bild Resettet")
                select(ordernumber.get())
            except Exception as e:
                logger.exception(e)
                logger.info("Bild konnte nicht zurückgesetzt werden")
        else:
            return

    IrfanFrame = tk.Frame(
        parent,
        highlightbackground="blue",
        highlightthickness=2,
    )
    # IrfanFrame.pack_propagate(0)
    if pack:
        IrfanFrame.pack(anchor="w")
    else:
        IrfanFrame.grid(row=gridy, column=gridx, columnspan=columnspan, rowspan=rowspan)
    buttonIrfan = tk.Button(IrfanFrame, text="IrfanView", command=openIrfan, width=20)
    buttonIrfan.pack(pady=5, fill="x")
    buttonReload = tk.Button(
        IrfanFrame, text="Reset zu Originalbild", command=reset, width=20
    )
    buttonReload.pack(pady=5, fill="x")


def setBackground():
    asin = Util.Jsonprocessing.getAsin(ordernumber.get(), delimiter)
    colordictS = Util.Config.getColorCodesSilver()
    colordictB = Util.Config.getColorCodesBlack()
    if asin in colordictB.keys():
        try:
            for item in vorschauobjekte:
                vorschauobjekte[item].configure(bg=colordictB[asin])
        except Exception as e:
            print(
                "Background kann nicht gesettet werden, tkinter bug ?, zur not programm neu starten, ich weis nicht wie ich das behebe"
                + str(e)
            )
    else:
        try:
            for item in vorschauobjekte:
                vorschauobjekte[item].configure(bg=colordictS[asin])
        except Exception as e:
            print(
                "Background kann nicht gesettet werden, tkinter bug ?, zur not programm neu starten, ich weis nicht wie ich das behebe"
                + str(e)
            )


def intermediate(evt):
    try:  # keine auswahl durch liste wechseln ignorieren
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        ordernumber.set(value)
        select(value)
    except:
        pass


def intermediateSelect(evt):
    select(ordernumber.get())


def invert():
    try:
        global currentPatternImage
        if invertVar.get() == 1:
            patternName = pattern.get()
            if patternName == "Es gibt kein Bild":
                print("es gibt nichts zu invertieren")
                return None
            vorschaubildpattern = Image.open(patternName)
            vorschaubildpattern = Util.Imageprocessing.invertAlt(vorschaubildpattern)
            vorschaubildpattern = Util.Imageprocessing.schwarzweis(
                colorscheme.get(), vorschaubildpattern, thresh.get(), threshhold.get()
            )
            vorschaubildpattern = Util.Imageprocessing.invertAlt(vorschaubildpattern)

        else:
            updatePreviewUI(None)
            return

        currentPatternImage = vorschaubildpattern
        asin = Util.Jsonprocessing.getAsin(ordernumber.get(), delimiter)
        colordictS = Util.Config.getColorCodesSilver()
        if asin in colordictS.keys():
            vorschaubildpattern = Util.Imageprocessing.weisZuSilber(vorschaubildpattern)

        size = Util.Imageprocessing.getscale(
            anzeigenzielbreite, anzeigenmaxhöhe, vorschaubildpattern
        )
        vorschaubildpattern = vorschaubildpattern.resize(
            size, Image.Resampling.BILINEAR
        )
        # zwischenablage des bilds zum geben an process
        vorschaubildpattern = ImageTk.PhotoImage(vorschaubildpattern)
        for item in vorschauobjekte:
            if "Bild" in item:
                vorschauobjekte[item].configure(image=vorschaubildpattern)
                vorschauobjekte[item].image = vorschaubildpattern
    except Exception as e:
        print("Problem beim Funktionsaufruf des invertierens" + str(e))


def textHandlingGUI(currentOrder, guistyle, builddict):
    fonts = Util.Jsonprocessing.getFont(currentOrder, delimiter)
    color = Util.Jsonprocessing.getEngravingColor(currentOrder, delimiter)
    if color == "Silber":
        color = Util.Config.getUIColor()
        color = color["SilberColor"]
    else:
        color = "gray0"  # schwarz
    if fonts in f.families():
        if guistyle == "Senkrecht":
            fonts = f.Font(family=fonts, size=10)
        else:
            fonts = f.Font(family=fonts, size=20)
        fontnotfound.configure(text="")
    else:
        fontnotfound.configure(
            text="SCHRIFTART NICHT GEFUNDEN, Sieht eventuell anders aus" + fonts
        )
        if guistyle == "Senkrecht":
            fonts = ("Arial", 10)
        else:
            fonts = ("Arial", 20)
    for item in vorschauobjekte:
        if "Text" in item:
            texttoscreen = Util.Jsonprocessing.getTextGUI(
                currentOrder, builddict[item], delimiter
            )
            if guistyle == "Senkrecht":
                texttoscreen = texttoscreen.replace(" ", " \n")

            vorschauobjekte[item].configure(text=texttoscreen, font=fonts, fg=color)


def imageHandlingGUI(currentOrder):
    global currentPatternImage
    counter = 0
    for item in vorschauobjekte:
        if "Bild" in item:
            try:
                patternName = pattern.get()
                counter += 1
                vorschaubildpattern = Image.open(patternName)
                asin = Util.Jsonprocessing.getAsin(currentOrder, delimiter)
                colordictS = Util.Config.getColorCodesSilver()
                vorschaubildpattern = Util.Imageprocessing.schwarzweis(
                    colorscheme.get(),
                    vorschaubildpattern,
                    thresh.get(),
                    threshhold.get(),
                )
                # zwischenablage des bilds zum geben an process
                currentPatternImage = vorschaubildpattern
                patternpfad = pattern.get()
                if pfadzuallenmotiven not in patternpfad:
                    allemotive = True
                else:
                    allemotive = False
                if (
                    asin in colordictS.keys()
                    and (
                        colorscheme.get() == "Schwarz-Weiß"
                        or colorscheme.get() == "Schwarz-Weiß Dithering"
                    )
                    and allemotive == False
                ):
                    vorschaubildpattern = Util.Imageprocessing.invertAlt(
                        vorschaubildpattern
                    )
                    vorschaubildpattern = Util.Imageprocessing.weisZuSilber(
                        vorschaubildpattern
                    )

                size = Util.Imageprocessing.getscale(
                    anzeigenzielbreite, anzeigenmaxhöhe, vorschaubildpattern
                )
                vorschaubildpattern = vorschaubildpattern.resize(
                    size, Image.Resampling.BILINEAR
                )

                vorschaubildpattern = ImageTk.PhotoImage(vorschaubildpattern)
                vorschauobjekte[item].configure(image=vorschaubildpattern)
                vorschauobjekte[item].image = vorschaubildpattern
                invertVar.set(0)

            except Exception as e:
                if not patternName == "Es gibt kein Bild":
                    print(patternName + " wurde nicht gefunden, bitte überprüfen")


def select(currentOrder):
    if profiling == True:
        prof = profile.Profile()
        prof.enable()
    global patternliste
    global objekte
    ordernumber.set(currentOrder)
    try:
        _, farbe = Util.Config.getXMLConfig(template.get().split(".")[0])
        colorscheme.set(farbe["farbart"])

    except:
        print("fehler beim lesen des Templates")
    guiTemplateToUse = Util.Config.getXMLConfig(template.get().split(".")[0])[1]["gui"]
    patternliste, hits = Util.Jsonprocessing.getOnlyPattern(
        ordernumber.get(), delimiter, guiTemplateToUse
    )
    if not hits == 0:
        update_dropdown()
        pattern.set(patternliste[-1])
    else:
        patternliste = ["Es gibt kein Bild"]
        update_dropdown()
        pattern.set("Es gibt kein Bild")
        mehrereAusgewaehlteBilder.configure(text="", fg="#9f1d35")

    # gibts mehrere Bilder?
    if hits > 1:
        mehrereAusgewaehlteBilder.configure(
            text="Mehrere Bilder gefunden", fg="#9f1d35"
        )
    else:
        mehrereAusgewaehlteBilder.configure(text="", fg="#9f1d35")

    try:
        comment.configure(
            text=Util.Jsonprocessing.getComments(ordernumber.get(), delimiter)
        )
    except:
        print("Kommentar kann nicht angezeigt werden")

    # erstmaliges belegen der GUI
    previewUI(None)
    updateAugmentUI(objekte)
    if profiling == True:
        prof.disable()
        stats = pstats.Stats(prof).strip_dirs().sort_stats("cumtime")
        stats.print_stats(10)  # top 10 rows


def update_dropdown():
    menu = dropPattern["menu"]
    menu.delete(0, "end")
    for string in patternliste:
        menu.add_command(
            label=string, command=tk._setit(pattern, string, updatePreviewUI)
        )


def process():
    global order
    global currentPatternImage

    # ListOfOrdersStillToDo.remove(ordernumber.get())
    if Util.Jsonprocessing.getIfOnlyText(ordernumber.get()) or bildistda == False:
        currentPatternImage = None
    else:
        # workaround fuer bilder auf schwarzem hintergrund
        if invertVar.get() == 1:
            dummy = Util.Imageprocessing.invertAlt(currentPatternImage)
            dummy.save("Util/pattern.png")
        else:
            currentPatternImage.save("Util/pattern.png")

    Orders.processxml(
        template.get(),
        delimiter,
        ordernumber.get(),
        targetbreitelb,
        maxhoehelb,
        currentPatternImage,
        skalierungsfaktor,
        pixelinmm,
    )
    try:
        subprocess.Popen(
            [
                pfadzulightburn,
                str(os.getcwd()) + "\\Util\\output.lbrn",
            ]
        )
    except Exception as e:
        print(e)
        print("Lightburn kann nicht gestartet werden")
    window.update()
    # window.destroy()


if __name__ == "__main__":
    logging.basicConfig(filename="logs.log", level=logging.INFO)
    print("Version: 0.5")
    # initiale Belegung der Variablen
    order = None
    ListOfOrdersStillToDo = []
    ListOfAvailableTemplates = Util.Gather.getTemplates()
    if not ListOfAvailableTemplates:
        print("Es wurden keine Templates gefunden")
    ListOfColors = [
        "Schwarz-Weiß Dithering",
        "Schwarz-Weiß",
        "Graustufen",
        "Original",
        "Cropped Original",
    ]
    ListOfThreshholding = [
        "Otsu's thresholding after Gaussian filtering",
        "Adaptive Mean Threshholding",
        "Adaptive Gaussian Thresholding",
        "Global Thresholding",
    ]
    currentOrder = ""
    patternliste = ["Keine Auswahl"]
    csv = Util.Gather.parseCsv(inputfile, orderIdSpaltenName)
    currentPatternImage = None

    i = 1
    for item in csv:
        try:
            if not nodownload == "True":
                Util.Gather.downloadAndUnpack(
                    item[zipdownloadspalte],
                    item[orderIdSpaltenName],
                )
                print("Download: " + str(i) + " von " + str(len(csv)))
                i += 1
            ListOfOrdersStillToDo.append(item[orderIdSpaltenName])
        except Exception as e:

            print(
                "Der Download mit der nummer {nummer} hat nicht funktioniert".format(
                    nummer=i
                )
            )
            i += 1

    while True:
        # Setup Main Window
        window = tk.Tk()

        window.protocol("WM_DELETE_WINDOW", quit)
        window.title("Lightburn Preperation, Dynamic Preview 0.1")
        # window.geometry("1000x1000")
        ordernumber = tk.StringVar()
        ordernumber.set(ListOfOrdersStillToDo[0])
        colorscheme = tk.StringVar()
        colorscheme.set("Graustufen")
        template = tk.StringVar()
        template.set(standardTemplate)
        pattern = tk.StringVar()
        pattern.set("nochkeinsda")

        thresh = tk.StringVar()
        thresh.set("Otsu's thresholding after Gaussian filtering")
        invertVar = tk.IntVar()
        invertVar.set(0)

        overallFrame = tk.Frame(
            window,
            highlightbackground="red",
            highlightthickness=2,
        )
        overallFrame.grid(row=1, column=1, sticky="nesw")
        # overallFrame.pack(side="left", anchor="nw")

        overallFrame.grid_rowconfigure(2, minsize=anzeigenmaxhöhe + 170, weight=2)
        overallFrame.grid_columnconfigure(2, minsize=anzeigenzielbreite + 50, weight=1)
        overallFrame.grid_columnconfigure(3, minsize=anzeigenzielbreite + 50, weight=1)

        extendoFrame = tk.Frame(
            window,
            highlightbackground="green",
            highlightthickness=2,
        )
        extendoFrame.grid(row=1, column=2, sticky="nw")
        # extendoFrame.pack(side="left", anchor="nw")
        extendoFrame.rowconfigure(0, weight=1)
        extendoFrame.columnconfigure(0, weight=1)
        comment = tk.Label(overallFrame, text="", wraplength=250)
        comment.grid(row=3, column=3, columnspan=1)

        # Vorschaubild für den User
        vorschaubildFrame = tk.Frame(
            overallFrame,
            width=anzeigenzielbreite + 10,
            height=anzeigenmaxhöhe + 100,
            highlightbackground="blue",
            highlightthickness=2,
        )
        # vorschaubildFrame.grid(row=2, column=3, sticky="nsw")
        vorschaubildUser = tk.Label(
            vorschaubildFrame,
        )
        vorschaubildUser.pack()
        bildbezeichnungVorschau = tk.Label(vorschaubildFrame, text="Vorschaubild")
        bildbezeichnungVorschau.pack()

        # ErrorFrame
        frameError = tk.Frame(
            overallFrame,
            width=200,
            height=200,
            highlightbackground="blue",
            highlightthickness=2,
        )
        frameError.grid(row=1, column=1, columnspan=3, sticky="new")
        fontnotfound = tk.Label(frameError, font=("Arial", 20), wraplength=500)
        fontnotfound.pack()
        mehrereAusgewaehlteBilder = tk.Label(frameError, font=("Arial", 20))
        mehrereAusgewaehlteBilder.pack()

        # Selectframe
        frame = tk.Frame(overallFrame, padx=10)
        frame.grid(row=2, column=1, sticky="nsew")
        selectlist = tk.Listbox(
            frame,
            width=30,
            # height=int(anzeigenmaxhöhe / 10) + 3,
        )
        selectlist.pack(side="left", fill="y")
        scrollbar = tk.Scrollbar(frame, orient="vertical")
        scrollbar.config(command=selectlist.yview)
        scrollbar.pack(side="right", fill="y")
        selectlist.config(yscrollcommand=scrollbar.set)
        for item in ListOfOrdersStillToDo:
            selectlist.insert("end", item)
        selectlist.bind("<<ListboxSelect>>", intermediate)

        # gui previewframe
        previewFrame = tk.Frame(
            overallFrame,
            width=anzeigenzielbreite,
            height=anzeigenmaxhöhe,
            highlightbackground="blue",
            highlightthickness=2,
        )
        # dropdownmenue fuer template
        configFrame = tk.Frame(
            overallFrame, highlightbackground="blue", highlightthickness=2
        )
        configFrame.grid(row=3, column=1, columnspan=2, sticky="new", pady=10)
        dropTemplate = tk.OptionMenu(
            configFrame,
            template,
            *ListOfAvailableTemplates,
            command=intermediateSelect,
        )
        dropTemplate.config(width=20)
        dropTemplate.pack(anchor="w")

        patternFrame = tk.Frame(
            overallFrame, highlightbackground="blue", highlightthickness=2
        )
        # patternFrame.grid(row=4, column=1, columnspan=2, sticky="new", pady=10)
        # dropdown zur bildauswahl
        dropPattern = tk.OptionMenu(
            configFrame, pattern, *patternliste, command=updatePreviewUI
        )
        dropPattern.pack(anchor="w")

        dropThresh = tk.OptionMenu(
            configFrame, thresh, *ListOfThreshholding, command=updatePreviewUI
        )
        dropThresh.config()
        dropThresh.pack(anchor="w")

        # select(ListOfOrdersStillToDo[0])
        # dropdownmenu fuer Vorschaubild schwarzweis
        dropColor = tk.OptionMenu(
            configFrame, colorscheme, *ListOfColors, command=updatePreviewUI
        )
        dropColor.config(width=20)
        dropColor.pack(anchor="w")
        threshhold = tk.Scale(
            configFrame, from_=0, to=255, orient=tk.HORIZONTAL, length=160
        )
        threshhold.set(127)
        threshhold.bind("<ButtonRelease-1>", updatePreviewUI)
        threshhold.pack(anchor="w")
        invertbutton = tk.Checkbutton(
            configFrame, text="Inverted", variable=invertVar, command=invert
        )
        invertbutton.pack(anchor="w", padx=30)

        startButton = tk.Button(
            overallFrame,
            text="Ausgewählte Bestellung Starten",
            command=process,
        )
        startButton.grid(row=5, column=1)
        previewFrame.grid(row=2, column=2, sticky="nsew", padx=10)

        IrfanUI(configFrame, 1, 4, 1, 1, pack=True)
        previewUI(None)
        objekte = augmentUI(extendoFrame)

        select(ListOfOrdersStillToDo[0])
        # window.eval("tk::PlaceWindow . center")

        window.mainloop()
