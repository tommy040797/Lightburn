# -*- coding: utf-8 -*-
import Util.Config
import Util.Gather
import Util.Imageprocessing
import Util.Order as Orders
import tkinter as tk
from tkinter import font
from PIL import ImageTk, Image
import subprocess
import Util.Jsonprocessing
import os
import cProfile as profile
import pstats

# TODO:  verfügbare aktionen für config dokumentieren, UI Ordnen, regex für filter, invertieren, schieberegler helligkeit kontrast gamma

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

profiling = False


def colorchange(dummy):
    global currentPatternImage
    if Util.Jsonprocessing.getIfOnlyText(ordernumber.get()):
        return None
    patternName = pattern.get()
    vorschaubildpattern = Image.open(patternName)
    size2 = Util.Imageprocessing.getscale(
        anzeigenzielbreite, anzeigenmaxhöhe, vorschaubildpattern
    )
    vorschaubildpattern = vorschaubildpattern.resize(size2, Image.Resampling.BILINEAR)
    vorschaubildpattern = Util.Imageprocessing.schwarzweis(
        colorscheme.get(), vorschaubildpattern, thresh.get()
    )
    size2 = Util.Imageprocessing.getscale(
        anzeigenzielbreite, anzeigenmaxhöhe, vorschaubildpattern
    )
    vorschaubildpattern = vorschaubildpattern.resize(size2, Image.Resampling.BILINEAR)
    # zwischenablage des bilds zum geben an process
    currentPatternImage = vorschaubildpattern
    vorschaubildpattern = ImageTk.PhotoImage(vorschaubildpattern)
    patternvorschauUser.configure(image=vorschaubildpattern)
    patternvorschauUser.image = vorschaubildpattern


def bildauswahl(bild):
    global currentPatternImage
    if Util.Jsonprocessing.getIfOnlyText(ordernumber.get()):
        return None
    try:
        vorschaubildpattern = Image.open(bild)
        size = Util.Imageprocessing.getscale(
            anzeigenzielbreite, anzeigenmaxhöhe, vorschaubildpattern
        )
        vorschaubildpattern = vorschaubildpattern.resize(
            size, Image.Resampling.BILINEAR
        )
        vorschaubildpattern = Util.Imageprocessing.schwarzweis(
            colorscheme.get(), vorschaubildpattern, thresh.get()
        )
        size = Util.Imageprocessing.getscale(
            anzeigenzielbreite, anzeigenmaxhöhe, vorschaubildpattern
        )
        vorschaubildpattern = vorschaubildpattern.resize(
            size, Image.Resampling.BILINEAR
        )
        # zwischenablage des bilds zum geben an process
        currentPatternImage = vorschaubildpattern
        vorschaubildpattern = ImageTk.PhotoImage(vorschaubildpattern)
        patternvorschauUser.configure(image=vorschaubildpattern)
        patternvorschauUser.image = vorschaubildpattern
    except:
        print(bild + " wurde nicht gefunden, bitte überprüfen")
        return


# war super dumm eine riesen update methode zu machen ............
def select(currentOrder):
    global patternliste
    # wenn wir kein bild haben:
    _, farbe = Util.Config.getXMLConfig(template.get().split(".")[0])
    colorscheme.set(farbe["farbart"])
    if Util.Jsonprocessing.getIfOnlyText(currentOrder):
        # vorschau
        patternliste = ["Es gibt kein Bild"]
        pattern.set("Es gibt kein Bild")
        update_dropdown()
        previewName = Util.Jsonprocessing.getPreviewImage(currentOrder)
        vorschaubild = Image.open("Zips/" + currentOrder + "/" + previewName)
        size = Util.Imageprocessing.getscale(
            anzeigenzielbreite, anzeigenmaxhöhe, vorschaubild
        )
        vorschaubild = vorschaubild.resize(size, Image.Resampling.BILINEAR)
        vorschaubild = ImageTk.PhotoImage(vorschaubild)
        vorschaubildUser.configure(image=vorschaubild)
        vorschaubildUser.image = vorschaubild

        # Patternbehandlung
        mehrereAusgewaehlteBilder.configure(text="", fg="#9f1d35")
        textAbove = Util.Jsonprocessing.getFirstLine(currentOrder)
        textBelow = Util.Jsonprocessing.getThirdLine(currentOrder)
        patternvorschauUser.configure(
            image="", text=Util.Jsonprocessing.getSecondLine(currentOrder)
        )
        fonts = Util.Jsonprocessing.getFont(currentOrder)
        color = Util.Jsonprocessing.getEngravingColor(currentOrder)
        if color == "Silber":
            color = "dim gray"
        else:
            color = "gray0"
        if fonts in font.families():
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
                font="Arial",
            )
            textunterbild.configure(text=textBelow, fg=color, font="Arial")
            textueberbild.configure(text=textAbove, fg=color, font="Arial")
    else:
        # bildhandling wenn bilder vorhanden sind
        previewName = Util.Jsonprocessing.getPreviewImage(currentOrder)
        patternliste, hits = Util.Jsonprocessing.getOnlyPattern(currentOrder, delimiter)
        update_dropdown()
        pattern.set(patternliste[-1])

        patternName = pattern.get()
        vorschaubild = Image.open("Zips/" + currentOrder + "/" + previewName)
        # vorschaubildpattern = Image.open(patternName)
        size = Util.Imageprocessing.getscale(
            anzeigenzielbreite, anzeigenmaxhöhe, vorschaubild
        )
        vorschaubild = vorschaubild.resize(size, Image.Resampling.BILINEAR)
        vorschaubild = ImageTk.PhotoImage(vorschaubild)
        vorschaubildUser.configure(image=vorschaubild)
        vorschaubildUser.image = vorschaubild
        bildauswahl(patternName)

        # texthandling
        if hits > 1:
            mehrereAusgewaehlteBilder.configure(
                text="Mehrere Bilder gefunden", fg="#9f1d35"
            )
        else:
            mehrereAusgewaehlteBilder.configure(text="", fg="#9f1d35")
        textAbove = Util.Jsonprocessing.getTextAbove(currentOrder)
        textBelow = Util.Jsonprocessing.getTextBelow(currentOrder)
        fonts = Util.Jsonprocessing.getFont(currentOrder)
        color = Util.Jsonprocessing.getEngravingColor(currentOrder)
        if color == "Silber":
            color = "dim gray"
        else:
            color = "gray0"
        if fonts in font.families():
            fontnotfound.configure(text="")
            textunterbild.configure(text=textBelow, fg=color, font=(fonts,))
            textueberbild.configure(text=textAbove, fg=color, font=(fonts,))
        else:
            fontnotfound.configure(
                text="SCHRIFTART NICHT GEFUNDEN, Sieht eventuell anders aus"
            )
            textunterbild.configure(text=textBelow, fg=color, font="Arial")
            textueberbild.configure(text=textAbove, fg=color, font="Arial")
    ordernumber.set(currentOrder)
    comment.configure(text=Util.Jsonprocessing.getComments(ordernumber.get()))


def update_dropdown():
    menu = dropPattern["menu"]
    menu.delete(0, "end")
    for string in patternliste:
        menu.add_command(label=string, command=tk._setit(pattern, string, bildauswahl))


def process():
    global order
    global currentPatternImage
    window.destroy()
    # ListOfOrdersStillToDo.remove(ordernumber.get())
    if Util.Jsonprocessing.getIfOnlyText(ordernumber.get()):
        currentPatternImage = None
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
    subprocess.call(
        [
            pfadzulightburn,
            str(os.getcwd()) + "\\Util\\output.lbrn",
        ]
    )


if __name__ == "__main__":
    if profiling == True:
        prof = profile.Profile()
        prof.enable()
    order = None
    ListOfOrdersStillToDo = []
    ListOfAvailableTemplates = Util.Gather.getTemplates()
    ListOfColors = [
        "Schwarz-Weiß Dithering",
        "Schwarz-Weiß",
        "Graustufen",
        "Original",
        "Cropped Original",
    ]
    ListOfThreshholding = [
        "Adaptive Mean Threshholding",
        "Adaptive Gaussian Thresholding",
        "Otsu's thresholding after Gaussian filtering",
    ]
    currentOrder = ""
    patternliste = ["Keine Auswahl"]
    csv = Util.Gather.parseCsv(inputfile, orderIdSpaltenName)
    for item in csv:
        if not nodownload == "True":
            Util.Gather.downloadAndUnpack(
                item[zipdownloadspalte],
                item[orderIdSpaltenName],
            )
        ListOfOrdersStillToDo.append(item[orderIdSpaltenName])
    currentPatternImage = None

    while len(ListOfOrdersStillToDo) != 0:
        # Setup Main Window
        window = tk.Tk()
        window.protocol("WM_DELETE_WINDOW", quit)
        window.title("Lightburn Preperation")
        window.geometry("800x500")
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
        thresh.set("Adaptive Gaussian Thresholding")

        # Vorschaubild für den User
        vorschaubildUser = tk.Label(window)
        vorschaubildUser.pack(side="right", fill="both", expand="yes")
        bildbezeichnungVorschau = tk.Label(window, text="Vorschaubild")
        bildbezeichnungVorschau.pack()
        patternvorschauUser = tk.Label(window)
        patternvorschauUser.pack(side="right", fill="both", expand="yes")
        textunterbild = tk.Label(window)
        textunterbild.pack()
        textueberbild = tk.Label(window)
        textueberbild.pack()
        fontnotfound = tk.Label(window)
        fontnotfound.pack()
        mehrereAusgewaehlteBilder = tk.Label(window)
        mehrereAusgewaehlteBilder.pack()
        bildbezeichnungPattern = tk.Label(window, text="Pattern")
        bildbezeichnungPattern.pack()

        # select(ListOfOrdersStillToDo[0])
        patternvorschauUser
        # dropdownmenü um auftrag auszuwaehlen
        drop = tk.OptionMenu(
            window, ordernumber, *ListOfOrdersStillToDo, command=select
        )
        drop.pack()

        # dropdownmenue fuer template
        dropTemplate = tk.OptionMenu(
            window, template, *ListOfAvailableTemplates, command=colorchange
        )
        dropTemplate.pack()

        # dropdown zur bildauswahl
        dropPattern = tk.OptionMenu(window, pattern, *patternliste, command=bildauswahl)
        dropPattern.pack()

        dropThresh = tk.OptionMenu(
            window, thresh, *ListOfThreshholding, command=colorchange
        )
        dropThresh.pack()

        select(ListOfOrdersStillToDo[0])
        # dropdownmenu fuer Vorschaubild schwarzweis
        dropColor = tk.OptionMenu(
            window, colorscheme, *ListOfColors, command=colorchange
        )
        dropColor.pack()

        startButton = tk.Button(
            window,
            text="Ausgewählte Bestellung Starten",
            command=process,
        )
        startButton.pack()

        select(ListOfOrdersStillToDo[0])
        if profiling == True:
            prof.disable()
            stats = pstats.Stats(prof).strip_dirs().sort_stats("cumtime")
            stats.print_stats(10)  # top 10 rows
        window.mainloop()

    if profiling == True:
        prof.disable()
        stats = pstats.Stats(prof).strip_dirs().sort_stats("cumtime")
        stats.print_stats(10)  # top 10 rows
