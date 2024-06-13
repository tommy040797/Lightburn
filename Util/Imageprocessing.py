# import cv2 as cv
from PIL import Image
import cv2 as cv
import numpy as np
from PIL import ImageOps


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


def weisDurchsichtig(img):
    x = np.asarray(img.convert("RGBA")).copy()

    x[:, :, 3] = (255 * (x[:, :, :3] != 255).any(axis=2)).astype(np.uint8)

    return Image.fromarray(x)


def schwarzweis(cholorscheme, vorschaubildpattern, thresh):
    if cholorscheme == "Graustufen":
        try:
            vorschaubildpattern = durchsichtigWeis(vorschaubildpattern)
        except:
            pass
        # imagetk photoimage nimmt kein schwarzweisalpha bild, sondern nur rgba
        vorschaubildpattern = vorschaubildpattern.convert("LA")
        vorschaubildpattern = cropImage(vorschaubildpattern)
        vorschaubildpattern = vorschaubildpattern.convert("RGBA")
        vorschaubildpattern = weisDurchsichtig(vorschaubildpattern)
    elif cholorscheme == "Schwarz-Weiß Dithering":
        try:
            vorschaubildpattern = durchsichtigWeis(vorschaubildpattern)
            pass
        except:
            pass
        vorschaubildpattern = vorschaubildpattern.convert("1")
        vorschaubildpattern = cropImage(vorschaubildpattern)
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
        # array = cropImageAltAlt(array)
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
        vorschaubildpattern = cropImage(vorschaubildpattern)
        vorschaubildpattern = vorschaubildpattern.convert("RGBA")
        vorschaubildpattern = weisDurchsichtig(vorschaubildpattern)
    elif cholorscheme == "Cropped Original":
        vorschaubildpattern = cropImage(vorschaubildpattern)
        vorschaubildpattern = weisDurchsichtig(vorschaubildpattern)

    return vorschaubildpattern


def cropImage(img):
    invert_im = img.convert("RGB")
    invert_im = ImageOps.invert(invert_im)
    imageBox = invert_im.getbbox()
    cropped = img.crop(imageBox)
    cropped = cropped.convert("RGBA")
    return cropped


def invertStep(image):
    return image.point(lambda p: 255 - p)


def invert(img):
    try:
        r, g, b, a = img.split()

        r, g, b, a = map(invertStep, (r, g, b, a))
        img2 = Image.merge(img.mode, (r, g, b, a))
        return img2
    except:
        print("problem beim invertieren")


def invertAlt(img):
    try:
        r, g, b, a = img.split()

        r, g, b = map(invertStep, (r, g, b))
        img2 = Image.merge(img.mode, (r, g, b, a))
        return img2
    except:
        print("problem beim invertieren")
