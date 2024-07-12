import configparser
import codecs


def getFilterConfig():
    config = configparser.ConfigParser()
    config.read("filter.ini")
    return config._sections["Default"]


def getXMLConfig(name):
    config = configparser.ConfigParser()
    config.read("Templates/" + name + ".ini", encoding="UTF-8")
    return config._sections["Automatic"], config._sections["Default"]


def getLaserColors():
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read("laserColorParameters.ini")
    return config._sections["Silber"], config._sections["Schwarz"]


def getConfig():
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read("config.ini", encoding="UTF-8")
    return config._sections["Default"]


def getGuiConfig():
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read("gui.ini")
    # config.read("gui.ini")
    return config._sections["Default"]


def getColorCodesBlack():
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read("colorCodes.ini")
    return config._sections["Schwarz"]


def getColorCodesSilver():
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read("colorCodes.ini")
    return config._sections["Silber"]


def getUIColor():
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read("Gui.ini")
    return config._sections["UI"]


def getAugmentedUI():
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read("Gui.ini")
    return config._sections["CustomElements"]
