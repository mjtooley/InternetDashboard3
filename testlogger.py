import logging
import logging.config
from logging.handlers import RotatingFileHandler

logging.config.fileConfig('logging.conf')

# create logger
logger = logging.getLogger('simpleExample')

hdlr = RotatingFileHandler('testlogger.log', maxBytes=1000000000, backupCount=2)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)
# 'application' code
logger.debug('debug message')
logger.info('info message')
logger.warn('warn message')
logger.error('error message')
logger.critical('critical message')
