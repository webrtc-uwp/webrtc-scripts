import os
from enum import Enum
import shutil 
import glob

import config
from logger import Logger
from settings import Settings
from utility import Utility
from system import System
from errors import NO_ERROR
from helper import convertToPlatformPath

#TODO: Return error code and terminate script!!!

class Cleanup:
  @classmethod
  def init(cls):
    """
      Inits logger
    """
    cls.logger = Logger.getLogger('Cleanup')

  @classmethod
  def cleanOutput(cls, target='*', platform='*', cpu='*', configuration='*'):
    """
      Deletes output folders.
      :param target: Target (ortc, webrtc or * )
      :param platform: Platform (win, winuwp or *)
      :param cpu: CPU (arm, x86, x64 or *)
      :param configuration: Release (debug, release or *)
      :return ret: True if output folders deletion was successful, otherwise False
    """
    ret = True

    if target == '': target = '*'
    if platform == '': platform = '*'
    if cpu == '': cpu = '*'
    if configuration == '': configuration = '*'

    #Switch working directory to root webrtc folder
    Utility.pushd(Settings.webrtcPath)
    foldersToDelete = list()

    #Generate path name for deletion from gn output folder, based on template from config. 
    #It can contain * do delete output folders i.e. for all CPUs for specific target ./out/webrtc_winuwp_*_Debug
    gnFolderToClean = config.GN_TARGET_OUTPUT_PATH.replace('[GN_OUT]', config.GN_OUTPUT_PATH).replace('[TARGET]',target).replace('[PLATFORM]',platform).replace('[CPU]',cpu).replace('[CONFIGURATION]',configuration)
    #Generate folder name for deletion from  output folder, based on template from config
    outputFolderToClean = convertToPlatformPath(config.BUILT_LIBS_DESTINATION_PATH.replace('[BUILD_OUTPUT]',config.BUILD_OUTPUT_PATH).replace('[TARGET]',target).replace('[PLATFORM]',platform).replace('[CPU]',cpu).replace('[CONFIGURATION]',configuration))
    
    #Convert path to host os style, and add all folders that satisfy condition for deletion to the foldersToDelete
    for folderPath in glob.iglob(convertToPlatformPath(gnFolderToClean)):
      foldersToDelete.append(folderPath)
    
    #Convert path to host os style, and add all folders that satisfy condition for deletion to the foldersToDelete
    for folderPath in glob.iglob(convertToPlatformPath(outputFolderToClean)):
      foldersToDelete.append(folderPath)

    #Delete all folders marked for deletion
    for folderToDelete in foldersToDelete:
      try:
        shutil.rmtree(folderToDelete)
      except Exception as error:
        ret = False
        cls.logger.error(str(error))
        cls.logger.error('Failed deleting folders')

    Utility.popd()

    return ret

  @classmethod
  def cleanUserDef(cls):
    """
      Deletes userdef.py file.
      TODO: RECREATE USERDEF AFTER DELETION
      :return ret: True if useddef.py is deleted, otherwise False
    """
    ret = True
    result = System.recreateUserDef()
    if result != NO_ERROR:
      ret = False

    return ret

  @classmethod
  def cleanIdls(cls):
    """
      Deletes .flg and files generated from idl.
      :return ret: True if .flg and generated files are deleted, otherwise False
    """
    ret = True

    Utility.pushd(Settings.webrtcPath)

    try:
      if os.path.exists(convertToPlatformPath(config.IDL_FLAG_OUTPUT_PATH)):
        for flgFilePath in glob.iglob(os.path.join(convertToPlatformPath(config.IDL_FLAG_OUTPUT_PATH), '*.flg')):
          os.remove(flgFilePath)
      
      if os.path.exists(convertToPlatformPath(config.IDL_GENERATED_FILES_OUTPUT_PATH)):
        shutil.rmtree(convertToPlatformPath(config.IDL_GENERATED_FILES_OUTPUT_PATH))
    except Exception as error:
      ret = False
      cls.logger.error(str(error))
      cls.logger.error('Failed removing files generated with idl compiler.')

    Utility.popd()

    return ret

  @classmethod
  def cleanPrepare(cls):
    """
      Remove all changes made during preparation process
      TODO: There is an issue wuth deleting junction links
    """
    ret = True
      
    #Switch working directory to root webrtc folder
    Utility.pushd(Settings.webrtcPath)

    try:
      #for source, destination in (dict in config.FILES_TO_COPY):
      for destination in [val for d in config.FILES_TO_COPY for val in d.values()]:
        if os.path.isfile(destination):
          os.remove(destination)

      #Remove links created for Ortc target
      Utility.deleteFolderLinks(config.FOLDERS_TO_LINK_ORTC)
      #Delete created folders for Ortc target
      Utility.deleteFolders(config.FOLDERS_TO_GENERATE_ORTC)

      #Remove links created for WebRtc target
      Utility.deleteFolderLinks(config.FOLDERS_TO_LINK)
      #Delete created folders for WebRtc target
      Utility.deleteFolders(config.FOLDERS_TO_GENERATE)

    except Exception as error:
      ret = False
      cls.logger.error(str(error))
      cls.logger.error('Failed reverting preparation changes')
      
    Utility.popd()

    return ret

  @classmethod
  def run(cls, action, target='*', platform='*', cpu='*', configuration='*'):
    """
      Performs cleanup for provided action and specific imput arguments.
      :param action: Action to perform (cleanOutput, cleanUserDef, cleanIdls or cleanPrepare)
      :param target: Target (ortc, webrtc or * )
      :param platform: Platform (win, winuwp or *)
      :param cpu: CPU (arm, x86, x64 or *)
      :param configuration: Release (debug, release or *)
      :return ret: True if clean was successful, otherwise False
    """
    ret = False

    if action == 'cleanOutput':
      ret = cls.cleanOutput(target, platform, cpu, configuration)

    if action == 'cleanUserDef':
      ret = cls.cleanUserDef()

    if action == 'cleanIdls':
      ret = cls.cleanIdls()

    if action == 'cleanPrepare':
      ret = cls.cleanPrepare()

    if ret:
      cls.logger.info('Cleanup action ' + action + ' is finished successfully for ' + target + ' ' + platform + ' ' + cpu + ' ' + configuration)
    else:
      cls.logger.error('Cleanup action ' + action + ' has failed for ' + target + ' ' + platform + ' ' + cpu + ' ' + configuration)
    return ret