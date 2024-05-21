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
