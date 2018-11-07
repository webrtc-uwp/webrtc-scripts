import os
from enum import Enum
import shutil 

import config
from logger import Logger
from settings import Settings
from utility import Utility

class Cleanup:
  @classmethod
  def init(cls):
    cls.logger = Logger.getLogger('Cleanup')

  @classmethod
  def run(cls):
    Utility.pushd(Settings.webrtcPath)
    if os.path.exists('out'):
        shutil.rmtree('out')

    if os.path.exists('BUILD_OUTPUT'):
        shutil.rmtree('BUILD_OUTPUT') 

    for path in config.FOLDERS_TO_GENERATE:
      if os.path.exists(path):
        shutil.rmtree(path) 

    """ Pass info if ortc is in game
    if (ortc):
      for path in config.FOLDERS_TO_GENERATE_ORTC:
        if os.path.exists(path):
          shutil.rmtree(path)  
    """
    Utility.popd()

