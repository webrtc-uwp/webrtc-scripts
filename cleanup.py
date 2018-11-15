import os
from enum import Enum
import shutil 
import glob

import config
from logger import Logger
from settings import Settings
from utility import Utility
from helper import convertToPlatformPath

class Cleanup:
  @classmethod
  def init(cls):
    cls.logger = Logger.getLogger('Cleanup')

  @classmethod
  def cleanOutput(cls):
    
    Utility.pushd(Settings.rootSdkPath)

    if os.path.exists(config.GN_OUTPUT_PATH):
      shutil.rmtree(config.GN_OUTPUT_PATH)

    if os.path.exists(config.BUILD_OUTPUT_PATH):
      shutil.rmtree(config.BUILD_OUTPUT_PATH)

    Utility.popd()

  @classmethod
  def cleanUserDef(cls):

    if os.path.isfile(Settings.userDefFilePath):
      os.remove(Settings.userDefFilePath) 

  @classmethod
  def cleanIdls(cls):

    Utility.pushd(Settings.webrtcPath)

    if os.path.exists(convertToPlatformPath(config.IDL_FLAG_OUTPUT_PATH)):
      for flgFilePath in glob.iglob(os.path.join(convertToPlatformPath(config.IDL_FLAG_OUTPUT_PATH), '*.flg')):
        os.remove(flgFilePath)
    
    if os.path.exists(convertToPlatformPath(config.IDL_GENERATED_FILES_OUTPUT_PATH)):
      shutil.rmtree(convertToPlatformPath(config.IDL_GENERATED_FILES_OUTPUT_PATH))

    Utility.popd()

  @classmethod
  def cleanPrepare(cls):

    Utility.pushd(Settings.webrtcPath)

    #for source, destination in (dict in config.FILES_TO_COPY):
    for destination in [val for d in config.FILES_TO_COPY for val in d.values()]:
      if os.path.isfile(destination):
        os.remove(destination)

    Utility.deleteFolderLinks(config.FOLDERS_TO_LINK_ORTC)
    Utility.removeFolders(config.FOLDERS_TO_GENERATE_ORTC)

    Utility.deleteFolderLinks(config.FOLDERS_TO_LINK)
    Utility.removeFolders(config.FOLDERS_TO_GENERATE)


  @classmethod
  def run(cls, action):

    if action == 'cleanOutput':
      cls.cleanOutput()

    if action == 'cleanUserDef':
      cls.cleanUserDef()

    if action == 'cleanIdls':
      cls.cleanIdls()

    if action == 'cleanPrepare':
      cls.cleanPrepare()

