import logging
import subprocess
import platform
import os.path
from datetime import datetime

from settings import Settings

if  platform.system().lower() == 'windows':
  import winutility
  winutility.enable_vt_mode()
  
class ColoredFormatter(logging.Formatter):

  BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

  color_level_dict = {
            logging.DEBUG: (None, WHITE, False),
            logging.INFO: (None, GREEN, False),
            logging.WARNING: (None, YELLOW, False),
            logging.ERROR: (None, RED, False),
            logging.CRITICAL: (RED, WHITE, False),
        }

  RESET_SEQUECE = "\033[0m"
  CSI_SEQUENCE = "\033["

  def __init__(self, msg, dateFormat = "%Y-%m-%d %H:%M:%S", use_color = True):
    logging.Formatter.__init__(self, msg, dateFormat)
    self.use_color = use_color

  def colorize(self,message,params):
    bg, fg, bold = params
    parts = []
    if bg != None:
      parts.append(str(bg + 40))
    if fg != None:
      parts.append(str(fg + 30))
    if bold:
        parts.append('1')
    if parts:
        message = ''.join((self.CSI_SEQUENCE, ';'.join(parts),
                            'm', message, self.RESET_SEQUECE))
    return message

  def format(self, record):
    if (self.use_color):
      record.levelname = self.colorize(record.levelname,self.color_level_dict[record.levelno])
      record.msg = self.colorize(record.msg,self.color_level_dict[record.levelno])
    return logging.Formatter.format(self, record)


class Logger:

  formatter = None #ColoredFormatter(FORMAT)
  loggerHandle = None #logging.StreamHandler()
  #loggerHandle.setFormatter(formatter)
  @classmethod
  def SetUp(cls):

    if cls.loggerHandle == None:
      if Settings.logToFile == "":
        cls.loggerHandle = logging.StreamHandler()
      else:
        filename = Settings.logToFile
        if os.path.isfile(filename) and  not Settings.overwriteLogFile:
          filename = os.path.splitext(filename)[0] + '_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S' + os.path.splitext(filename)[1])
        cls.loggerHandle = logging.FileHandler(filename,'w')

    if cls.formatter == None and Settings.logFormat != "":
      if Settings.logToFile == "":
        cls.formatter = ColoredFormatter(Settings.logFormat)
      else:
        cls.formatter = logging.Formatter(Settings.logFormat)
      cls.loggerHandle.setFormatter(cls.formatter)

  @classmethod
  def getLogger(cls,name):
    logger=logging.getLogger(name)
    if logger.handlers == []:
      logger.setLevel(logging.getLevelName(Settings.logLevel))
      logger.addHandler(cls.loggerHandle)
    return logger

  @staticmethod
  def printColorMessage(message,textColor = ColoredFormatter.RED, background = None):
    coloredMessage = ''.join((ColoredFormatter.CSI_SEQUENCE, (str(textColor + 30)),
                            'm', message, ColoredFormatter.RESET_SEQUECE))
    print(coloredMessage)


