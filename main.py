# -*- coding: utf-8 -*-
import Util.Config
import Util.Gather
import Util.Imageprocessing
import Util.Order as Orders
import tkinter as tk
from tkinter import font as f
from PIL import ImageTk, Image
import subprocess
import Util.Jsonprocessing
import os
import cProfile as profile
import pstats

# TODO: UI Ordnen, regex für filter, invertieren, schieberegler helligkeit kontrast gamma, template name egal machen, template nicht da fehlermeldung, grau statt weis, translation größe etc.

# Config lesen
try:
    configdict = Util.Config.getConfig()
    inputfile = configdict["Inputfile"]
    zipdownloadspalte = configdict["NameDerSpalteFuerZipDownload"]
    anzeigenzielbreite = int(configdict["GuiBildbreite"])
    anzeigenmaxhöhe = int(configdict["GuiBildhoehe"])
    nodownload = configdict["DebugNoDownload"]

    targetbreitelb = int(configdict["Flaschenbreite"])
    maxhoehelb = int(configdict["Flaschenhoehe"])

    standardTemplate = configdict["Standardtemplate"]
    delimiter = configdict["delimiterFuerConfig"]
    pfadzulightburn = configdict["PfadZuLightburn"]
    orderIdSpaltenName = configdict["ID-Spaltenname"]
except:
    print(
        "Standardconfig wurde nicht gefunden, oder ein Fehler liegt vor, Programm wird beendet"
    )
    quit()

bildistda = True
profiling = False


def setBackground(asin, colordictB, colordictS):
    global patternvorschauFrame
    global patternvorschauUser
    global textueberbild
    global textunterbild
    if asin in colordictB.keys():
        try:
            patternvorschauFrame.configure(bg=colordictB[asin])
            textueberbild.configure(bg=colordictB[asin])
            textunterbild.configure(bg=colordictB[asin])
            patternvorschauUser.configure(bg=colordictB[asin])
        except Exception as e:
            print(
                "Background kann nicht gesettet werden, tkinter bug ?, zur not programm neu starten, ich weis nicht wie ich das behebe"
                + str(e)
            )
    else:
        try:
            patternvorschauFrame.configure(bg=colordictS[asin])
            textueberbild.configure(bg=colordictS[asin])
            textunterbild.configure(bg=colordictS[asin])
            patternvorschauUser.configure(bg=colordictS[asin])
        except Exception as e:
            print(
                "Background kann nicht gesettet werden, tkinter bug ?, zur not programm neu starten, ich weis nicht wie ich das behebe"
                + str(e)
            )


def intermediate(evt):

    w = evt.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    ordernumber.set(value)
    select(value)


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
                colorscheme.get(), vorschaubildpattern, thresh.get()
            )
            vorschaubildpattern = Util.Imageprocessing.invertAlt(vorschaubildpattern)

        else:
            bildauswahl(None)
            return

        currentPatternImage = vorschaubildpattern
        asin = Util.Jsonprocessing.getAsin(ordernumber.get())
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
        # currentPatternImage = vorschaubildpattern
        vorschaubildpattern = ImageTk.PhotoImage(vorschaubildpattern)
        patternvorschauUser.configure(image=vorschaubildpattern)
        patternvorschauUser.image = vorschaubildpattern
    except Exception as e:
        print("Problem beim Funktionsaufruf des invertierens" + str(e))


def bildauswahl(dummy):

    global bildistda
    global currentPatternImage
    if Util.Jsonprocessing.getIfOnlyText(ordernumber.get()):
        return None
    erg, hits = Util.Jsonprocessing.getOnlyPattern(ordernumber.get(), delimiter)
    if hits == 0:
        bildistda = False
        patternvorschauUser.configure(image="")
        patternvorschauUser.image = None
        textHandlingGUI(ordernumber.get())

    else:
        bildistda = True
        try:
            patternName = pattern.get()
            vorschaubildpattern = Image.open(patternName)
            asin = Util.Jsonprocessing.getAsin(ordernumber.get())
            colordictS = Util.Config.getColorCodesSilver()

            vorschaubildpattern = Util.Imageprocessing.schwarzweis(
                colorscheme.get(), vorschaubildpattern, thresh.get()
            )
            # zwischenablage des bilds zum geben an process
            currentPatternImage = vorschaubildpattern
            if asin in colordictS.keys():
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
            patternvorschauUser.configure(image=vorschaubildpattern)
            patternvorschauUser.image = vorschaubildpattern
            invertVar.set(0)

        except Exception as e:
            print(patternName + " wurde nicht gefunden, bitte überprüfen" + str(e))
            return


def vorschaubild(currentOrder):
    global vorschaubildUser
    try:
        previewName = Util.Jsonprocessing.getPreviewImage(currentOrder)
        vorschaubild = Image.open("Zips/" + currentOrder + "/" + previewName)
        size = Util.Imageprocessing.getscale(
            anzeigenzielbreite, anzeigenmaxhöhe, vorschaubild
        )
        vorschaubild = vorschaubild.resize(size, Image.Resampling.BILINEAR)
        vorschaubild = ImageTk.PhotoImage(vorschaubild)
        vorschaubildUser.configure(image=vorschaubild)
        vorschaubildUser.image = vorschaubild
    except:
        print("Amazon vorschaubild konnte nicht angezeigt werden")


def textHandlingGUI(currentOrder):
    global textunterbild
    global textueberbild
    try:
        textAbove = Util.Jsonprocessing.getTextAbove(currentOrder)
        textBelow = Util.Jsonprocessing.getTextBelow(currentOrder)
        fonts = Util.Jsonprocessing.getFont(currentOrder)
        color = Util.Jsonprocessing.getEngravingColor(currentOrder)
    except:
        print(
            "Bei einer Bestellung mit nur Text konnte mindestens ein Text nicht geladen werden, oder die Font oder color konnte nicht geladen werden"
        )
    if Util.Jsonprocessing.getIfOnlyText(currentOrder):
        try:
            textAbove = Util.Jsonprocessing.getFirstLine(currentOrder)
            textBelow = Util.Jsonprocessing.getThirdLine(currentOrder)
            patternvorschauUser.configure(
                image="", text=Util.Jsonprocessing.getSecondLine(currentOrder)
            )

        except:
            print(
                "Bei einer Bestellung mit nur Text konnte mindestens ein Text nicht geladen werden"
            )
        try:

            if color == "Silber":
                color = Util.Config.getUIColor()
                color = color["SilberColor"]
            else:
                color = "gray0"
            if fonts in f.families():
                fonts = f.Font(family=fonts, size=20)
                fontnotfound.configure(text="")
                patternvorschauUser.configure(
                    image="",
                    text=Util.Jsonprocessing.getSecondLine(currentOrder),
                    fg=color,
                    font=fonts,
                )
                textunterbild.configure(text=textBelow, fg=color, font=fonts)
                textueberbild.configure(text=textAbove, fg=color, font=fonts)
            else:
                fontnotfound.configure(
                    text="SCHRIFTART NICHT GEFUNDEN, Sieht eventuell anders aus"
                )
                patternvorschauUser.configure(
                    image="",
                    text=Util.Jsonprocessing.getSecondLine(currentOrder),
                    fg=color,
                    font=("Arial", 20),
                )
                textunterbild.configure(text=textBelow, fg=color, font=("Arial", 20))
                textueberbild.configure(text=textAbove, fg=color, font=("Arial", 20))
        except:
            print(
                "Error bei der Fontverwaltung und setzen der Texte, bitte Programmierer konsultieren"
            )
    else:
        try:
            if color == "Silber":
                color = Util.Config.getUIColor()
                color = color["SilberColor"]
            else:
                color = "gray0"
            if fonts in f.families():
                fonts = f.Font(family=fonts, size=20)
                fontnotfound.configure(text="")
                textunterbild.configure(text=textBelow, fg=color, font=fonts)
                textueberbild.configure(text=textAbove, fg=color, font=fonts)
            else:
                fontnotfound.configure(
                    text="SCHRIFTART NICHT GEFUNDEN, Sieht eventuell anders aus"
                )
                textunterbild.configure(text=textBelow, fg=color, font=("Arial", 20))
                textueberbild.configure(text=textAbove, fg=color, font=("Arial", 20))
        except:
            print(
                "Error bei der Fontverwaltung und setzen der Texte, bitte Programmierer konsultieren"
            )


def select(currentOrder):
    if profiling == True:
        prof = profile.Profile()
        prof.enable()
    global patternliste
    try:
        _, farbe = Util.Config.getXMLConfig(template.get().split(".")[0])
        colorscheme.set(farbe["farbart"])
    except:
        print("fehler beim lesen des Templates")

    # wenn wir kein bild haben:
    if Util.Jsonprocessing.getIfOnlyText(currentOrder):
        # vorschau
        patternliste = ["Es gibt kein Bild"]
        update_dropdown()
        pattern.set("Es gibt kein Bild")
        vorschaubild(currentOrder)
        # Patternbehandlung
        mehrereAusgewaehlteBilder.configure(text="", fg="#9f1d35")
        # patternvorschauUser.configure(bg=None)
        textHandlingGUI(currentOrder)
    else:
        # bildhandling wenn bilder vorhanden sind

        previewName = Util.Jsonprocessing.getPreviewImage(currentOrder)
        patternliste, hits = Util.Jsonprocessing.getOnlyPattern(currentOrder, delimiter)
        if not hits == 0:
            update_dropdown()
            pattern.set(patternliste[-1])
        bildauswahl(None)
        vorschaubild(currentOrder)

        # texthandling
        if hits > 1:
            mehrereAusgewaehlteBilder.configure(
                text="Mehrere Bilder gefunden", fg="#9f1d35"
            )
        else:
            mehrereAusgewaehlteBilder.configure(text="", fg="#9f1d35")
        textHandlingGUI(currentOrder)
    ordernumber.set(currentOrder)

    try:
        comment.configure(text=Util.Jsonprocessing.getComments(ordernumber.get()))
    except:
        print("Kommentar kann nicht angezeigt werden")
    asin = Util.Jsonprocessing.getAsin(ordernumber.get())
    colordictS = Util.Config.getColorCodesSilver()
    colordictB = Util.Config.getColorCodesBlack()
    setBackground(asin, colordictB, colordictS)
    if profiling == True:
        # prof.disable()
        stats = pstats.Stats(prof).strip_dirs().sort_stats("cumtime")
        stats.print_stats(10)  # top 10 rows


def update_dropdown():
    menu = dropPattern["menu"]
    menu.delete(0, "end")
    for string in patternliste:
        menu.add_command(label=string, command=tk._setit(pattern, string, bildauswahl))


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
    print("Version: 0.2")
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
                + str(e)
            )
            i += 1

    while len(ListOfOrdersStillToDo) != 0:
        # Setup Main Window
        window = tk.Tk()
        window.protocol("WM_DELETE_WINDOW", quit)
        window.title("Lightburn Preperation")
        window.geometry("1000x700")
        ordernumber = tk.StringVar()
        ordernumber.set(ListOfOrdersStillToDo[0])
        colorscheme = tk.StringVar()
        colorscheme.set("Graustufen")
        template = tk.StringVar()
        template.set(standardTemplate)
        pattern = tk.StringVar()
        pattern.set("")
        comment = tk.Label(window, text="")
        comment.pack()
        thresh = tk.StringVar()
        thresh.set("Otsu's thresholding after Gaussian filtering")
        invertVar = tk.IntVar()
        invertVar.set(0)

        # Vorschaubild für den User
        vorschaubildUser = tk.Label(window)
        vorschaubildUser.pack(side="right", fill="both", expand="yes")
        bildbezeichnungVorschau = tk.Label(window, text="Vorschaubild")
        bildbezeichnungVorschau.pack()

        # Patternvorschau
        patternvorschauFrame = tk.Frame(window)
        patternvorschauFrame.pack(side="right")
        textueberbild = tk.Label(patternvorschauFrame)
        textueberbild.pack()
        patternvorschauUser = tk.Label(
            patternvorschauFrame,
            # width=anzeigenzielbreite,
            # height=anzeigenmaxhöhe,
        )
        patternvorschauUser.pack(fill="x", expand="no")
        textunterbild = tk.Label(patternvorschauFrame)
        textunterbild.pack()

        fontnotfound = tk.Label(window)
        fontnotfound.pack()
        mehrereAusgewaehlteBilder = tk.Label(window)
        mehrereAusgewaehlteBilder.pack()
        bildbezeichnungPattern = tk.Label(window, text="Pattern")
        bildbezeichnungPattern.pack()

        # dropdownmenü um auftrag auszuwaehlen
        # drop = tk.OptionMenu(
        # window, ordernumber, *ListOfOrdersStillToDo, command=select
        # )
        # drop.pack()

        frame = tk.Frame(window)
        frame.pack()
        list = tk.Listbox(
            frame,
            width=30,
            height=10,
        )
        list.pack(side="left", fill="y")
        scrollbar = tk.Scrollbar(frame, orient="vertical")
        scrollbar.config(command=list.yview)
        scrollbar.pack(side="right", fill="y")
        list.config(yscrollcommand=scrollbar.set)
        for item in ListOfOrdersStillToDo:
            list.insert("end", item)
        list.bind("<<ListboxSelect>>", intermediate)
        # dropdownmenue fuer template
        dropTemplate = tk.OptionMenu(
            window, template, *ListOfAvailableTemplates, command=bildauswahl
        )
        dropTemplate.pack()

        # dropdown zur bildauswahl
        dropPattern = tk.OptionMenu(window, pattern, *patternliste, command=bildauswahl)
        dropPattern.pack()

        dropThresh = tk.OptionMenu(
            window, thresh, *ListOfThreshholding, command=bildauswahl
        )
        dropThresh.pack()

        select(ListOfOrdersStillToDo[0])
        # dropdownmenu fuer Vorschaubild schwarzweis
        dropColor = tk.OptionMenu(
            window, colorscheme, *ListOfColors, command=bildauswahl
        )
        dropColor.pack()

        startButton = tk.Button(
            window,
            text="Ausgewählte Bestellung Starten",
            command=process,
        )
        startButton.pack()
        invertbutton = tk.Checkbutton(
            window, text="Inverted", variable=invertVar, command=invert
        )
        invertbutton.pack()
        select(ListOfOrdersStillToDo[0])

        window.mainloop()
