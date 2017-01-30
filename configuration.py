import ConfigParser

config = ConfigParser.RawConfigParser(allow_no_value=True)
config.read("configuration.ini")

def getmsm_ids():
    return (config.get('Options', 'msm_ids').split(','))

def getAsnList():
    return( config.get('Options', 'asns').split(','))

def getMongoServer():
    return(config.get('Options', 'mongoServer'))

def getMongoDB():
    return(config.get('Options','mongoDB'))

def getCarbonServer():
    return(config.get('Options','carbonServer'))

def getWindow():
    window = config.get('Options', 'WINDOW')
    return int(window)
