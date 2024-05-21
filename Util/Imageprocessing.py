# import cv2 as cv
from PIL import Image
import cv2 as cv
import numpy as np


def getscale(targetwidth, maxhoehe, img):
    originalw, originalh = img.size
    factor = originalw / targetwidth
    targeth = int(originalh / factor)
    targetw = targetwidth
    if int(originalh / factor) > maxhoehe:
        factor = originalh / maxhoehe
        targetw = int(originalw / factor)
        targeth = int(originalh / factor)
    return (int(targetw), int(targeth))


def durchsichtigWeis(img):
    datas = img.getdata()
    newData = []
    for item in datas:
        if item[3] == 0:
            newData.append((255, 255, 255, 255))
        else:
            newData.append(item)

    img.putdata(newData)
    return img


def weisDurchsichtig2(img):
    datas = img.getdata()
    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    return img


def weisDurchsichtig(img):
    width, height = img.size
    pixdata = img.load()

    for y in range(height):
        for x in range(width):
            if pixdata[x, y] == (255, 255, 255, 255):
                pixdata[x, y] = (255, 255, 255, 0)
    return img


def schwarzweis(cholorscheme, vorschaubildpattern, thresh):
    if cholorscheme == "Graustufen":
        try:
            vorschaubildpattern = durchsichtigWeis(vorschaubildpattern)
        except:
            pass
        # imagetk photoimage nimmt kein schwarzweisalpha bild, sondern nur rgba
        vorschaubildpattern = vorschaubildpattern.convert("LA")
        vorschaubildpattern = crop(vorschaubildpattern)
        vorschaubildpattern = vorschaubildpattern.convert("RGBA")
        vorschaubildpattern = weisDurchsichtig(vorschaubildpattern)
    elif cholorscheme == "Schwarz-Weiß Dithering":
        try:
            vorschaubildpattern = durchsichtigWeis(vorschaubildpattern)
            pass
        except:
            pass
        vorschaubildpattern = vorschaubildpattern.convert("1")
        vorschaubildpattern = cropAlt(vorschaubildpattern)
        vorschaubildpattern = vorschaubildpattern.convert("RGBA")

        vorschaubildpattern = weisDurchsichtig(vorschaubildpattern)
    elif cholorscheme == "Schwarz-Weiß":
        try:
            vorschaubildpattern = durchsichtigWeis(vorschaubildpattern)
        except:
            pass
        vorschaubildpattern = vorschaubildpattern.convert("RGB")
        array = np.array(vorschaubildpattern)
        array = cv.cvtColor(array, cv.COLOR_BGR2GRAY)
        array = cropAltAlt(array)
        match thresh:
            case "Global Thresholding":
                # vorschaubildpattern = cv.threshold(array, 127, 255, cv.THRESH_BINARY)
                pass
            case "Adaptive Mean Threshholding":
                vorschaubildpattern = cv.adaptiveThreshold(
                    array, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2
                )
            case "Adaptive Gaussian Thresholding":
                vorschaubildpattern = cv.adaptiveThreshold(
                    array, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2
                )
            case "Otsu's thresholding after Gaussian filtering":
                blur = cv.GaussianBlur(array, (5, 5), 0)
                _, vorschaubildpattern = cv.threshold(
                    blur, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU
                )
            case _:
                vorschaubildpattern = cv.adaptiveThreshold(
                    array, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2
                )
        vorschaubildpattern = Image.fromarray(vorschaubildpattern)
        vorschaubildpattern = crop(vorschaubildpattern)
        vorschaubildpattern = vorschaubildpattern.convert("RGBA")
        vorschaubildpattern = weisDurchsichtig(vorschaubildpattern)
    elif cholorscheme == "Cropped Original":
        vorschaubildpattern = crop(vorschaubildpattern)

    return vorschaubildpattern


def crop(img):
    array = np.array(img)
    try:
        blacky, blackx, dummy = np.where(array != 255)
    except:
        blacky, blackx = np.where(array != 255)
    top, bottom = blacky[0], blacky[-1]

    left, right = min(blackx), max(blackx)

    img = array[top:bottom, left:right]
    im_pil = Image.fromarray(img)
    return im_pil


def cropAlt(img):
    array = np.array(img)
    try:
        blacky, blackx, dummy = np.where(array != True)
    except:
        blacky, blackx = np.where(array != True)
    top, bottom = blacky[0], blacky[-1]

    left, right = min(blackx), max(blackx)

    img = array[top:bottom, left:right]
    im_pil = Image.fromarray(img)
    return im_pil


def cropAltAlt(img):
    array = img
    try:
        blacky, blackx, dummy = np.where(array != 255)
    except:
        blacky, blackx = np.where(array != 255)
    top, bottom = blacky[0], blacky[-1]

    left, right = min(blackx), max(blackx)

    img = array[top:bottom, left:right]
    return img
